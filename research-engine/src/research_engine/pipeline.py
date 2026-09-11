"""1→4단계 전체 파이프라인."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from .analysis import CaseAnalyzer
from .extract.extractor import Extractor
from .ingest import DocumentIngestor, OcrDocument, UserNote, apply_clarification, load_ocr_document
from .requirements import CaseRequirements, load_requirements
from .schema import CaseAnalysis, ClarificationRequest, ExtractionResult, ProcessedDocument, Timeline
from .timeline import TimelineBuilder


class ImageDocumentInput(BaseModel):
    doc_id: str
    file_name: str
    image_paths: list[str] = Field(min_length=1, description="한 문서의 사진들 (페이지 순서)")
    captured_at: datetime | None = None


class CaseInput(BaseModel):
    case_id: str
    case_type: str
    as_of: date
    documents: list[OcrDocument] = Field(default_factory=list, description="OCR이 끝난 문서")
    images: list[ImageDocumentInput] = Field(default_factory=list, description="OCR 엔진이 필요한 사진 입력")
    user_notes: list[UserNote] = Field(default_factory=list)


class PipelineResult(BaseModel):
    case_id: str
    case_type: str
    as_of: date
    documents: list[ProcessedDocument]
    clarifications: list[ClarificationRequest] = Field(description="사용자에게 되물을 질문 (priority 순)")
    extraction: ExtractionResult
    timeline: Timeline
    analysis: CaseAnalysis


class ResearchPipeline:
    def __init__(
        self,
        ingestor: DocumentIngestor | None = None,
        extractor: Extractor | None = None,
        timeline_builder: TimelineBuilder | None = None,
        analyzer: CaseAnalyzer | None = None,
        requirements: CaseRequirements | None = None,
    ):
        self.ingestor = ingestor or DocumentIngestor()
        self.extractor = extractor or Extractor()
        self.timeline_builder = timeline_builder or TimelineBuilder()
        self.analyzer = analyzer or CaseAnalyzer()
        self.requirements = requirements

    def run(self, case: CaseInput) -> PipelineResult:
        docs: list[ProcessedDocument] = []
        questions: list[ClarificationRequest] = []
        for ocr_doc in case.documents:
            res = self.ingestor.ingest(ocr_doc)
            docs.append(res.document)
            questions.extend(res.clarifications)
        for img in case.images:
            res = self.ingestor.ingest_images(img.doc_id, img.file_name, list(img.image_paths), img.captured_at)
            docs.append(res.document)
            questions.extend(res.clarifications)
        docs.extend(self.ingestor.ingest_user_note(n) for n in case.user_notes)
        return self.analyze_documents(case.case_id, case.case_type, case.as_of, docs, questions)

    def analyze_documents(
        self,
        case_id: str,
        case_type: str,
        as_of: date,
        docs: list[ProcessedDocument],
        questions: list[ClarificationRequest],
    ) -> PipelineResult:
        """2~4단계. 되묻기 답변을 반영한 뒤 다시 돌릴 때도 쓴다."""
        requirements = self.requirements or load_requirements(case_type)
        extraction = self.extractor.extract(docs, as_of)
        timeline = self.timeline_builder.build(extraction, requirements)
        pending = [q for q in questions if q.status == "pending"]
        analysis = self.analyzer.analyze(case_id, requirements, as_of, docs, extraction, timeline, pending)
        all_questions = {q.request_id: q for q in questions + extraction.clarifications}
        return PipelineResult(
            case_id=case_id,
            case_type=case_type,
            as_of=as_of,
            documents=docs,
            clarifications=sorted(all_questions.values(), key=lambda q: (q.status != "pending", q.priority)),
            extraction=extraction,
            timeline=timeline,
            analysis=analysis,
        )

    def answer(self, result: PipelineResult, request_id: str, answer: str) -> PipelineResult:
        """질문 하나에 답하고 2~4단계를 다시 계산한다 (한 번에 하나씩 묻는 흐름)."""
        request = next((q for q in result.clarifications if q.request_id == request_id), None)
        if request is None:
            raise KeyError(request_id)
        docs, questions = [], []
        for d in result.documents:
            if d.doc_id == request.doc_id:
                d, request = apply_clarification(d, request, answer)
            docs.append(d)
        for q in result.clarifications:
            questions.append(request if q.request_id == request_id else q)
        # 날짜 질문은 추출 단계에서 다시 생기므로 답한 것만 남긴다
        questions = [q for q in questions if q.kind.value != "ambiguous_date" or q.status != "pending"]
        return self.analyze_documents(result.case_id, result.case_type, result.as_of, docs, questions)


def load_case(path: str | Path) -> CaseInput:
    """case.json 로드. documents 항목이 문자열이면 같은 폴더의 OCR JSON 경로로 본다."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    docs = []
    for item in data.get("documents", []):
        docs.append(load_ocr_document(path.parent / item) if isinstance(item, str) else OcrDocument.model_validate(item))
    data["documents"] = docs
    return CaseInput.model_validate(data)
