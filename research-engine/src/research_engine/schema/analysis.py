"""4단계 산출물: 모순·공백 탐지 결과.

이 스키마는 기능 2(나의 사건 카드)와 행동 강령 매칭 엔진이 그대로 소비하도록 설계했다.
- ``Issue``          : 목업 '확인이 필요해요' 패널 한 항목
- ``ActionTrigger``  : 행동 강령 매칭 키. 검증된 절차 지식베이스는 이 키로만 조회한다
                       (proposal.md 108행 "사건 상태 → 무엇이 비어 있는가")
- ``CaseCard``       : 기능 2 카드 요약
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .extraction import ClaimSlot, Stage
from .provenance import SourceRef
from .timeline import StageStatus


class NliLabel(StrEnum):
    ENTAILMENT = "entailment"  # 일치 확인
    CONTRADICTION = "contradiction"  # 진술 불일치
    NEUTRAL = "neutral"  # 정보 부재 / 판단 보류


class NliScores(BaseModel):
    entailment: float = Field(ge=0.0, le=1.0)
    contradiction: float = Field(ge=0.0, le=1.0)
    neutral: float = Field(ge=0.0, le=1.0)

    def argmax(self) -> NliLabel:
        best = max(
            (self.entailment, NliLabel.ENTAILMENT),
            (self.contradiction, NliLabel.CONTRADICTION),
            (self.neutral, NliLabel.NEUTRAL),
        )
        return best[1]


class PairDecision(BaseModel):
    pair_id: str
    claim_a_id: str
    claim_b_id: str
    slot: ClaimSlot | None
    scores: NliScores
    model_label: NliLabel = Field(description="모델 argmax")
    label: NliLabel = Field(description="보수적 정책을 거친 최종 판정")
    downgraded: bool = False
    reasons: list[str] = Field(default_factory=list)
    model_name: str


class IssueCategory(StrEnum):
    INCONSISTENCY = "inconsistency"  # 자료끼리 어긋남
    UNVERIFIED = "unverified"  # 확인되지 않음
    MISSING = "missing"  # 빠진 정보
    UNREADABLE = "unreadable"  # 읽히지 않은 부분


ISSUE_CATEGORY_LABELS = {
    IssueCategory.INCONSISTENCY: "자료끼리 어긋남",
    IssueCategory.UNVERIFIED: "확인되지 않음",
    IssueCategory.MISSING: "빠진 정보",
    IssueCategory.UNREADABLE: "읽히지 않은 부분",
}


class GapCondition(StrEnum):
    CONFLICTING = "conflicting"  # NLI Contradiction 확정
    SUSPECTED_CONFLICT = "suspected_conflict"  # 모순 의심이나 근거 약해 Neutral로 내림
    CLAIMED_ONLY = "claimed_only"  # 진술만 있고 기록 자료 없음
    LOW_CONFIDENCE = "low_confidence"  # 추출 신뢰도 낮음 (교정 날짜 등)
    MISSING = "missing"  # 필수 항목이 어디에도 없음
    UNREADABLE = "unreadable"  # 원문이 읽히지 않음
    IDENTITY_UNCONFIRMED = "identity_unconfirmed"  # 동일인 여부 미확인
    TIME_GAP = "time_gap"  # 기록 공백 구간
    STAGE_SKIPPED = "stage_skipped"  # 중간 단계 자료 없음
    STAGE_STALLED = "stage_stalled"  # 현재 단계 이후 진행 기록 없음
    UNRECORDED_FACT = "unrecorded_fact"  # 사건 이후 나온 사실이 기록 자료에서 확인되지 않음


class SlotState(StrEnum):
    CONFIRMED = "confirmed"
    CLAIMED_ONLY = "claimed_only"
    CONFLICTING = "conflicting"
    LOW_CONFIDENCE = "low_confidence"
    UNREADABLE = "unreadable"
    MISSING = "missing"


class SlotStatus(BaseModel):
    slot: ClaimSlot
    label: str
    stage: Stage
    required: bool
    state: SlotState
    value: str | None = None
    claim_ids: list[str] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)


class ActionTrigger(BaseModel):
    """행동 강령 매칭 엔진 입력.

    ``key``는 ``{case_type}/{stage|-}/{slot|subject}/{condition}`` 형식으로 안정적이다.
    절차(무엇을·어디에·어떻게·언제까지)는 이 엔진이 만들지 않는다 — 검증된 지식베이스의 몫.
    """

    key: str
    case_type: str
    condition: GapCondition
    stage: Stage | None = None
    slot: ClaimSlot | None = None
    since: datetime | None = Field(default=None, description="관련 마지막 기록 시각 (기한 계산용)")
    elapsed_days: int | None = None
    evidence: list[SourceRef] = Field(default_factory=list)


class Issue(BaseModel):
    issue_id: str
    category: IssueCategory
    condition: GapCondition
    message: str
    stage: Stage | None = None
    slot: ClaimSlot | None = None
    sources: list[SourceRef] = Field(default_factory=list, description="근거가 된 원문 위치")
    checked_doc_ids: list[str] = Field(default_factory=list, description="'없음' 판단 시 확인한 문서")
    related_claim_ids: list[str] = Field(default_factory=list)
    related_event_ids: list[str] = Field(default_factory=list)
    related_entity_ids: list[str] = Field(default_factory=list)
    clarification_request_ids: list[str] = Field(default_factory=list)
    decision: PairDecision | None = None
    trigger: ActionTrigger
    priority: int = Field(description="낮을수록 먼저")


class CaseCard(BaseModel):
    """기능 2 '나의 사건 카드' 요약."""

    case_type: str
    case_type_label: str
    requirements_status: str
    stages: list[StageStatus]
    current_stage: Stage | None
    evidence_doc_count: int
    needs_confirmation_count: int
    slots_done: int
    slots_total: int
    next_trigger: ActionTrigger | None = None


class CaseAnalysis(BaseModel):
    case_id: str
    case_type: str
    as_of: date
    issues: list[Issue] = Field(default_factory=list)
    slot_statuses: list[SlotStatus] = Field(default_factory=list)
    pair_decisions: list[PairDecision] = Field(default_factory=list)
    action_triggers: list[ActionTrigger] = Field(default_factory=list)
    case_card: CaseCard
