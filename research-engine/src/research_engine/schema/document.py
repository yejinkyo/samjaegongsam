"""1단계 산출물: 전처리·OCR·레이아웃이 끝난 문서."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from .provenance import BBox, SourceRef


class DocumentType(StrEnum):
    JUDGMENT = "judgment"  # 판결문
    COMPLAINT = "complaint"  # 고소장·진정서
    STATEMENT = "statement"  # 진술서
    TRANSCRIPT = "transcript"  # 녹취록
    RECEIPT = "receipt"  # 영수증·이체확인증·접수증 (기관/업체 발급 기록)
    NOTICE = "notice"  # 수사결과·처분 통지서 (수사기관 발급 기록)
    MEMO = "memo"  # 손글씨 메모
    MESSENGER = "messenger"  # 메신저 대화 캡처
    NEWS = "news"  # 보도
    USER_NOTE = "user_note"  # 사용자가 직접 입력
    UNKNOWN = "unknown"


DOC_TYPE_LABELS: dict[DocumentType, str] = {
    DocumentType.JUDGMENT: "판결문",
    DocumentType.COMPLAINT: "고소장·진정서",
    DocumentType.STATEMENT: "진술서",
    DocumentType.TRANSCRIPT: "녹취록",
    DocumentType.RECEIPT: "영수증·확인증",
    DocumentType.NOTICE: "수사·처분 통지서",
    DocumentType.MEMO: "메모",
    DocumentType.MESSENGER: "메신저 대화",
    DocumentType.NEWS: "보도",
    DocumentType.USER_NOTE: "직접 입력",
    DocumentType.UNKNOWN: "미분류",
}


class EvidenceLevel(StrEnum):
    """자료의 증거 수준. 목업 배지 '확인됨 / 주장·미확인 / 내가 입력'과 대응."""

    RECORD = "record"  # 법원·수사기관·금융사 등 제3자가 발급한 기록
    STATEMENT = "statement"  # 당사자·관계인의 진술, 대화, 메모, 보도
    USER = "user"  # 사용자가 앱에서 직접 입력


EVIDENCE_RANK = {EvidenceLevel.RECORD: 3, EvidenceLevel.STATEMENT: 2, EvidenceLevel.USER: 1}


def evidence_level_for(doc_type: DocumentType) -> EvidenceLevel:
    if doc_type in (DocumentType.JUDGMENT, DocumentType.RECEIPT, DocumentType.NOTICE):
        return EvidenceLevel.RECORD
    if doc_type is DocumentType.USER_NOTE:
        return EvidenceLevel.USER
    return EvidenceLevel.STATEMENT


class Script(StrEnum):
    """글자 형태. 신뢰도 스코어링 피처로 쓰인다."""

    PRINTED = "printed"
    TYPEWRITER = "typewriter"
    HANDWRITTEN = "handwritten"
    UNKNOWN = "unknown"


class TextLine(BaseModel):
    """레이아웃 분석 후 한 줄. 원문 좌표 ↔ 텍스트 매핑의 최소 단위."""

    doc_id: str
    line_no: int = Field(ge=1, description="문서 전체 기준 줄 번호 (페이지를 넘어 이어짐)")
    page: int = Field(default=1, ge=1)
    bbox: BBox | None = None
    text: str = Field(description="OCR 원문. 자동 정제하지 않는다.")
    ocr_confidence: float = Field(ge=0.0, le=1.0)
    readability: float = Field(ge=0.0, le=1.0, description="신뢰도 스코어러가 매긴 판독 가능성")
    readable: bool
    script: Script = Script.UNKNOWN
    low_confidence_spans: list[tuple[int, int]] = Field(
        default_factory=list, description="줄 안에서 단어 신뢰도가 낮은 문자 구간"
    )
    origin: Literal["ocr", "user_clarified", "user_input"] = "ocr"

    def ref(self, char_start: int | None = None, char_end: int | None = None) -> SourceRef:
        quote = self.text if char_start is None else self.text[char_start:char_end]
        return SourceRef(
            source_doc_id=self.doc_id,
            page=self.page,
            source_line=self.line_no,
            source_bbox=self.bbox,
            char_start=char_start,
            char_end=char_end,
            quote=quote,
        )

    def span_confidence(self, start: int, end: int) -> float:
        """문자 구간의 신뢰도. 저신뢰 단어와 겹치면 절반으로 깎는다."""
        for s, e in self.low_confidence_spans:
            if s < end and start < e:
                return self.readability * 0.5
        return self.readability


class UnreadableRegion(BaseModel):
    """신뢰도가 낮아 '읽히지 않은 부분'으로 표시된 영역. 하위 단계 입력으로 쓰지 않는다."""

    region_id: str
    doc_id: str
    page: int
    line_no: int
    bbox: BBox | None
    readability: float
    reason: str
    ocr_guess: str = Field(description="참고용 OCR 추정 문자열. 추출·분석에 사용 금지")


class ClarificationKind(StrEnum):
    UNREADABLE_TEXT = "unreadable_text"
    DOCUMENT_TYPE = "document_type"
    AMBIGUOUS_DATE = "ambiguous_date"


class ClarificationRequest(BaseModel):
    """사용자에게 되묻는 질문 하나 (접근성 원칙: 한 화면에 하나만 묻는다)."""

    request_id: str
    kind: ClarificationKind
    question: str
    doc_id: str
    page: int = 1
    line_no: int | None = None
    bbox: BBox | None = None
    options: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list, description="앞뒤로 읽힌 줄 (판독 보조)")
    priority: int = 50
    status: Literal["pending", "answered", "skipped"] = "pending"
    answer: str | None = None


class PageInfo(BaseModel):
    page_no: int = Field(ge=1)
    width: float | None = None
    height: float | None = None
    image_ref: str | None = None


class ProcessedDocument(BaseModel):
    doc_id: str = Field(min_length=1)
    file_name: str
    doc_type: DocumentType
    doc_type_confidence: float = Field(ge=0.0, le=1.0)
    doc_type_scores: dict[str, float] = Field(default_factory=dict)
    evidence_level: EvidenceLevel
    captured_at: datetime | None = None
    pages: list[PageInfo] = Field(default_factory=list)
    lines: list[TextLine] = Field(default_factory=list)
    unreadable: list[UnreadableRegion] = Field(default_factory=list)

    def readable_lines(self) -> list[TextLine]:
        return [ln for ln in self.lines if ln.readable]

    def line(self, line_no: int) -> TextLine | None:
        for ln in self.lines:
            if ln.line_no == line_no:
                return ln
        return None
