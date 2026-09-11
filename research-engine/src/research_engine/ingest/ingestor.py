"""1단계 오케스트레이션: OCR 결과 → 줄 번호가 매겨진 ProcessedDocument + 되묻기 목록."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from ..schema import (
    DOC_TYPE_LABELS,
    ClarificationKind,
    ClarificationRequest,
    DocumentType,
    PageInfo,
    ProcessedDocument,
    Script,
    TextLine,
    UnreadableRegion,
    evidence_level_for,
)
from .classify import DocumentClassifier, KeywordDocClassifier
from .confidence import ReadabilityScorer
from .layout import group_words_into_lines, reading_order
from .ocr import OcrDocument, OcrEngine

UNREADABLE_QUESTION = "이 부분이 잘 읽히지 않습니다. 사진 속 글자를 보이는 대로 적어주시겠어요?"
DOC_TYPE_QUESTION = "이 자료는 어떤 종류인가요?"


class UserNote(BaseModel):
    """사용자가 앱에서 직접 적은 내용. 줄 번호가 출처가 된다."""

    note_id: str = Field(min_length=1)
    text: str
    created_at: datetime | None = None


class IngestResult(BaseModel):
    document: ProcessedDocument
    clarifications: list[ClarificationRequest] = Field(default_factory=list)


class DocumentIngestor:
    def __init__(
        self,
        classifier: DocumentClassifier | None = None,
        scorer: ReadabilityScorer | None = None,
        ocr_engine: OcrEngine | None = None,
        doc_type_min_confidence: float = 0.55,
    ):
        self.classifier = classifier or KeywordDocClassifier()
        self.scorer = scorer or ReadabilityScorer()
        self.ocr_engine = ocr_engine
        self.doc_type_min_confidence = doc_type_min_confidence

    def ingest_images(
        self,
        doc_id: str,
        file_name: str,
        image_paths: list[str | Path],
        captured_at: datetime | None = None,
        doc_type_hint: DocumentType | None = None,
    ) -> IngestResult:
        """사진 여러 장을 한 문서로 (페이지 순서 = 입력 순서)."""
        if self.ocr_engine is None:
            raise RuntimeError("이미지 입력에는 ocr_engine이 필요합니다")
        pages = [self.ocr_engine.recognize(Path(p), page_no=i) for i, p in enumerate(image_paths, start=1)]
        return self.ingest(
            OcrDocument(
                doc_id=doc_id,
                file_name=file_name,
                captured_at=captured_at,
                doc_type_hint=doc_type_hint,
                pages=pages,
            )
        )

    def ingest(self, ocr_doc: OcrDocument) -> IngestResult:
        lines: list[TextLine] = []
        unreadable: list[UnreadableRegion] = []
        pages: list[PageInfo] = []
        line_no = 0
        for page in ocr_doc.pages:
            pages.append(
                PageInfo(page_no=page.page_no, width=page.width, height=page.height, image_ref=page.image_ref)
            )
            raw_lines = page.lines or group_words_into_lines(page.words)
            for raw in reading_order(raw_lines):
                if not raw.text.strip():
                    continue
                line_no += 1
                script = raw.script or page.script_hint
                score = self.scorer.score_line(raw, script)
                readable = self.scorer.is_readable(score)
                lines.append(
                    TextLine(
                        doc_id=ocr_doc.doc_id,
                        line_no=line_no,
                        page=page.page_no,
                        bbox=raw.bbox,
                        text=raw.text,
                        ocr_confidence=raw.confidence,
                        readability=round(score, 4),
                        readable=readable,
                        script=script,
                        low_confidence_spans=self.scorer.low_confidence_spans(raw) if readable else [],
                    )
                )
                if not readable:
                    unreadable.append(
                        UnreadableRegion(
                            region_id=f"{ocr_doc.doc_id}:u{line_no}",
                            doc_id=ocr_doc.doc_id,
                            page=page.page_no,
                            line_no=line_no,
                            bbox=raw.bbox,
                            readability=round(score, 4),
                            reason=f"판독 신뢰도 {score:.2f} < 기준 {self.scorer.threshold:.2f}",
                            ocr_guess=raw.text,
                        )
                    )

        readable_text = [ln.text for ln in lines if ln.readable]
        handwritten = sum(1 for ln in lines if ln.script is Script.HANDWRITTEN) / max(len(lines), 1)
        clarifications: list[ClarificationRequest] = []
        if ocr_doc.doc_type_hint is not None:
            doc_type, doc_conf, scores = ocr_doc.doc_type_hint, 1.0, {ocr_doc.doc_type_hint.value: 1.0}
        else:
            pred = self.classifier.predict(readable_text, handwritten)
            doc_type, doc_conf, scores = pred.doc_type, pred.confidence, pred.scores
            if doc_conf < self.doc_type_min_confidence or doc_type is DocumentType.UNKNOWN:
                clarifications.append(
                    ClarificationRequest(
                        request_id=f"{ocr_doc.doc_id}:q-doctype",
                        kind=ClarificationKind.DOCUMENT_TYPE,
                        question=DOC_TYPE_QUESTION,
                        doc_id=ocr_doc.doc_id,
                        options=[
                            DOC_TYPE_LABELS[t]
                            for t in DocumentType
                            if t not in (DocumentType.UNKNOWN, DocumentType.USER_NOTE)
                        ],
                        priority=10,
                    )
                )

        doc = ProcessedDocument(
            doc_id=ocr_doc.doc_id,
            file_name=ocr_doc.file_name,
            doc_type=doc_type,
            doc_type_confidence=round(doc_conf, 4),
            doc_type_scores=scores,
            evidence_level=evidence_level_for(doc_type),
            captured_at=ocr_doc.captured_at,
            pages=pages,
            lines=lines,
            unreadable=unreadable,
        )
        clarifications.extend(self._unreadable_questions(doc))
        return IngestResult(document=doc, clarifications=clarifications)

    @staticmethod
    def _unreadable_questions(doc: ProcessedDocument) -> list[ClarificationRequest]:
        out = []
        for region in doc.unreadable:
            context = [
                ln.text for ln in doc.lines if ln.readable and abs(ln.line_no - region.line_no) == 1
            ]
            out.append(
                ClarificationRequest(
                    request_id=f"{region.region_id}:q",
                    kind=ClarificationKind.UNREADABLE_TEXT,
                    question=UNREADABLE_QUESTION,
                    doc_id=doc.doc_id,
                    page=region.page,
                    line_no=region.line_no,
                    bbox=region.bbox,
                    options=["읽을 수 없어요", "중요하지 않은 부분이에요"],
                    context=context,
                    priority=20,
                )
            )
        return out

    @staticmethod
    def ingest_user_note(note: UserNote) -> ProcessedDocument:
        lines = [
            TextLine(
                doc_id=note.note_id,
                line_no=i,
                text=text,
                ocr_confidence=1.0,
                readability=1.0,
                readable=True,
                origin="user_input",
            )
            for i, text in enumerate((t for t in note.text.splitlines() if t.strip()), start=1)
        ]
        return ProcessedDocument(
            doc_id=note.note_id,
            file_name="직접 입력",
            doc_type=DocumentType.USER_NOTE,
            doc_type_confidence=1.0,
            evidence_level=evidence_level_for(DocumentType.USER_NOTE),
            captured_at=note.created_at,
            pages=[PageInfo(page_no=1)],
            lines=lines,
        )


def apply_clarification(
    doc: ProcessedDocument, request: ClarificationRequest, answer: str
) -> tuple[ProcessedDocument, ClarificationRequest]:
    """사용자 답변 반영. 줄 번호·bbox는 그대로 두어 출처 추적이 끊기지 않게 한다."""
    request = request.model_copy(update={"status": "answered", "answer": answer})
    if request.kind is ClarificationKind.DOCUMENT_TYPE:
        label_to_type = {label: t for t, label in DOC_TYPE_LABELS.items()}
        doc_type = label_to_type.get(answer) or DocumentType(answer)
        doc = doc.model_copy(
            update={
                "doc_type": doc_type,
                "doc_type_confidence": 1.0,
                "evidence_level": evidence_level_for(doc_type),
            }
        )
        return doc, request
    if request.kind is ClarificationKind.UNREADABLE_TEXT and request.line_no is not None:
        if answer in request.options:  # "읽을 수 없어요" 등 — 읽히지 않은 상태 유지
            return doc, request
        lines = [
            ln.model_copy(
                update={"text": answer, "readable": True, "readability": 1.0, "origin": "user_clarified"}
            )
            if ln.line_no == request.line_no
            else ln
            for ln in doc.lines
        ]
        unreadable = [u for u in doc.unreadable if u.line_no != request.line_no]
        doc = doc.model_copy(update={"lines": lines, "unreadable": unreadable})
    elif request.kind is ClarificationKind.AMBIGUOUS_DATE and request.line_no is not None and request.context:
        if answer in request.options[-1:]:  # "모르겠어요" — 교정하지 않는다
            return doc, request
        raw = request.context[0]
        lines = [
            ln.model_copy(update={"text": ln.text.replace(raw, answer, 1), "origin": "user_clarified"})
            if ln.line_no == request.line_no and raw in ln.text
            else ln
            for ln in doc.lines
        ]
        doc = doc.model_copy(update={"lines": lines})
    return doc, request
