"""2단계 산출물: Event · Entity · Claim · Source 태깅 결과와 정규화된 시간."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, Field

from .document import ClarificationRequest, EvidenceLevel
from .provenance import Sourced


class Stage(StrEnum):
    """사건 진행 단계. 목업 타임라인 '발생→송금→신고→접수→수사→결과'."""

    OCCURRENCE = "occurrence"
    TRANSFER = "transfer"
    REPORT = "report"
    RECEIPT = "receipt"
    INVESTIGATION = "investigation"
    OUTCOME = "outcome"


STAGE_LABELS: dict[Stage, str] = {
    Stage.OCCURRENCE: "발생",
    Stage.TRANSFER: "송금",
    Stage.REPORT: "신고",
    Stage.RECEIPT: "접수",
    Stage.INVESTIGATION: "수사",
    Stage.OUTCOME: "결과",
}


# ── 시간 ────────────────────────────────────────────────────────────────


class TimeGranularity(StrEnum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    RANGE = "range"  # "며칠 전", "엊그제"처럼 폭이 있는 표현


GRANULARITY_RANK = {
    TimeGranularity.MINUTE: 0,
    TimeGranularity.HOUR: 1,
    TimeGranularity.DAY: 2,
    TimeGranularity.RANGE: 3,
    TimeGranularity.WEEK: 3,
    TimeGranularity.MONTH: 4,
    TimeGranularity.YEAR: 5,
}


class TimeKind(StrEnum):
    ABSOLUTE = "absolute"  # 2026년 6월 1일
    PARTIAL = "partial"  # 6월 1일 (연도는 기준일에서 추정)
    RELATIVE = "relative"  # 어제, 지난주 금요일, 3일 전
    CONTEXTUAL = "contextual"  # 시각만 있고 날짜는 앞선 날짜 줄에서 가져옴
    LUNAR = "lunar"  # 음력 8월 15일 → 양력 변환
    CORRECTED = "corrected"  # 오탈자/OCR 혼동 교정 후보 (반드시 확인 필요)
    UNRESOLVED = "unresolved"


class TimeCandidate(BaseModel):
    start: datetime
    end: datetime
    reason: str


class TimeValue(BaseModel):
    """정규화된 시간. 구간 [start, end) 로 표현해 서로 다른 입도끼리 겹침 비교가 가능하다."""

    raw: str
    start: datetime | None = None
    end: datetime | None = None
    granularity: TimeGranularity = TimeGranularity.DAY
    kind: TimeKind = TimeKind.ABSOLUTE
    approximate: bool = False
    anchor: date | None = None
    anchor_source: str | None = None
    candidates: list[TimeCandidate] = Field(default_factory=list)
    needs_confirmation: bool = False
    note: str | None = None

    @property
    def is_resolved(self) -> bool:
        return self.start is not None and self.end is not None

    def intervals(self) -> list[tuple[datetime, datetime]]:
        out: list[tuple[datetime, datetime]] = []
        if self.start is not None and self.end is not None:
            out.append((self.start, self.end))
        out.extend((c.start, c.end) for c in self.candidates)
        return out

    def compatible(self, other: TimeValue) -> bool | None:
        """두 시간이 같은 시점일 수 있는가. 비교 불가면 None."""
        a, b = self.intervals(), other.intervals()
        if not a or not b:
            return None
        return any(s1 < e2 and s2 < e1 for s1, e1 in a for s2, e2 in b)

    def gap_seconds(self, other: TimeValue) -> float | None:
        a, b = self.intervals(), other.intervals()
        if not a or not b:
            return None
        best = None
        for s1, e1 in a:
            for s2, e2 in b:
                gap = max(0.0, (s2 - e1).total_seconds(), (s1 - e2).total_seconds())
                best = gap if best is None else min(best, gap)
        return best

    def iso(self) -> str | None:
        """표시용 문자열. 폭이 있는 표현('밤', '3월 초순', '23시경')은 구간으로 보여준다."""
        if not self.is_resolved:
            return None
        s, e = self.start, self.end
        if self.approximate or self.granularity is TimeGranularity.RANGE:
            if self.granularity in (TimeGranularity.MINUTE, TimeGranularity.HOUR) and e - s < timedelta(days=1):  # type: ignore[operator]
                if e.minute:  # type: ignore[union-attr]
                    return f"{s:%Y-%m-%d %H:%M}~{e:%H:%M}"  # type: ignore[union-attr]
                end_hour = 24 if e.hour == 0 and e.date() > s.date() else e.hour  # type: ignore[union-attr]
                return f"{s:%Y-%m-%d %H}~{end_hour:02d}시" if end_hour > s.hour else f"{s:%Y-%m-%d %H시}~{e:%H시}"  # type: ignore[union-attr]
            last = e - timedelta(days=1)  # type: ignore[operator]
            return f"{s:%Y-%m-%d}~{last:%m-%d}" if s.year == last.year else f"{s:%Y-%m-%d}~{last:%Y-%m-%d}"  # type: ignore[union-attr]
        fmt = {
            TimeGranularity.MINUTE: "%Y-%m-%d %H:%M",
            TimeGranularity.HOUR: "%Y-%m-%d %H시",
            TimeGranularity.MONTH: "%Y-%m",
            TimeGranularity.YEAR: "%Y",
        }.get(self.granularity, "%Y-%m-%d")
        return self.start.strftime(fmt)  # type: ignore[union-attr]


# ── 엔티티 ──────────────────────────────────────────────────────────────


class EntityKind(StrEnum):
    PERSON = "person"
    NICKNAME = "nickname"
    ORGANIZATION = "organization"
    PLACE = "place"
    ACCOUNT = "account"
    PHONE = "phone"
    CASE_NUMBER = "case_number"
    RECEIPT_NUMBER = "receipt_number"


class EntityMention(BaseModel):
    mention_id: str
    doc_id: str
    kind: EntityKind
    name: Sourced[str]
    normalized: str = Field(description="coreference 비교용 정규화 값 (마스킹 문자는 *)")
    role: str | None = Field(default=None, description="피고인·고소인·판매자 등 문서 속 역할")


# ── 이벤트 ──────────────────────────────────────────────────────────────


class Event(BaseModel):
    """행위 + 시각."""

    event_id: str
    doc_id: str
    stage: Stage
    action: Sourced[str]
    time: Sourced[TimeValue] | None = None
    amount: Sourced[int] | None = None
    participant_mention_ids: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel
    action_kind: str | None = Field(default=None, description="같은 단계 안의 행위 종류 (sighting, contact_lost 등)")


# ── 주장 ────────────────────────────────────────────────────────────────


class ClaimSlot(StrEnum):
    """구조화 비교가 가능한 주장 항목. 4단계 모순·공백 탐지의 기본 단위."""

    INCIDENT_TIME = "incident_time"
    LAST_SEEN_TIME = "last_seen_time"
    LAST_CONTACT_TIME = "last_contact_time"
    TRANSFER_AMOUNT = "transfer_amount"
    TRANSFER_TIME = "transfer_time"
    ACCOUNT_NUMBER = "account_number"
    ACCOUNT_HOLDER = "account_holder"
    SHIPMENT_SENT = "shipment_sent"
    ITEM_RECEIVED = "item_received"
    TRACKING_NUMBER = "tracking_number"
    RECEIPT_NUMBER = "receipt_number"
    RECEIPT_TIME = "receipt_time"
    INVESTIGATOR = "investigator"
    INVESTIGATOR_CHANGE = "investigator_change"  # "담당자 바뀌었다고 함" — 이전 담당자 기록이 낡았을 수 있음
    CASE_NUMBER = "case_number"
    DECISION_TIME = "decision_time"
    DECISION_TYPE = "decision_type"


class Polarity(StrEnum):
    AFFIRM = "affirm"
    DENY = "deny"


class Claim(BaseModel):
    """누가 무엇을 진술했는가."""

    claim_id: str
    doc_id: str
    speaker: str
    speaker_basis: str = Field(
        description="화자 판단 근거: message_prefix | transcript_prefix | reported_speech | "
        "document_author | document_issuer"
    )
    speaker_mention_id: str | None = None
    content: Sourced[str]
    slot: ClaimSlot | None = None
    slot_value: str | None = Field(default=None, description="정규화 값 (금액=정수 문자열, 계좌=숫자/*)")
    slot_time: TimeValue | None = None
    value_is_speaker_self: bool = Field(default=False, description="'제 명의예요'처럼 값이 화자 자신")
    subject: str | None = Field(default=None, description="같은 슬롯 안에서 대상 구분 (예: 계좌 정규화 값)")
    polarity: Polarity = Polarity.AFFIRM
    said_at: TimeValue | None = None
    evidence_level: EvidenceLevel


class ExtractionResult(BaseModel):
    mentions: list[EntityMention] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    times: list[Sourced[TimeValue]] = Field(default_factory=list, description="검출된 모든 시간 표현")
    document_dates: dict[str, Sourced[TimeValue]] = Field(default_factory=dict)
    clarifications: list[ClarificationRequest] = Field(default_factory=list)
