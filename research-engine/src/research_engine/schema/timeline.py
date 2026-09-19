"""3단계 산출물: coreference로 통합된 엔티티와 시간축 타임라인."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .document import EvidenceLevel
from .extraction import EntityKind, Stage, TimeValue
from .provenance import SourceRef


class EntityLink(BaseModel):
    """같은 대상일 가능성은 있지만 병합하지 않은 연결 (확인 필요)."""

    other_entity_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class ResolvedEntity(BaseModel):
    entity_id: str
    kind: EntityKind
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    mention_ids: list[str] = Field(min_length=1)
    sources: list[SourceRef] = Field(min_length=1)
    merge_confidence: float = Field(ge=0.0, le=1.0)
    possible_same_as: list[EntityLink] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    timeline_event_id: str
    stage: Stage
    title: str
    time: TimeValue | None = None
    time_unknown: bool = False
    amount: int | None = None
    participant_entity_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(min_length=1)
    sources: list[SourceRef] = Field(min_length=1)
    evidence_level: EvidenceLevel
    needs_confirmation: bool = False
    flags: list[str] = Field(default_factory=list)


class StageState(StrEnum):
    DONE = "done"
    CURRENT = "current"  # 목업의 ◐ '지금 여기'
    PENDING = "pending"
    SKIPPED = "skipped"  # 뒤 단계 자료는 있는데 이 단계 자료가 없음


class StageStatus(BaseModel):
    stage: Stage
    label: str
    state: StageState
    timeline_event_ids: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel | None = None
    noted_only: bool = Field(
        default=False,
        description="이 단계에 이른 근거가 직접 적은 메모뿐이다 — 진행은 반영하되 그 단계의 자료가 있는 것은 아니다",
    )


class TimeGap(BaseModel):
    """기록이 비어 있는 구간."""

    start: datetime
    end: datetime
    hours: float
    before_event_id: str
    after_event_id: str


class Timeline(BaseModel):
    case_type: str
    events: list[TimelineEvent] = Field(default_factory=list)
    stages: list[StageStatus] = Field(default_factory=list)
    current_stage: Stage | None = None
    gaps: list[TimeGap] = Field(default_factory=list)
    entities: list[ResolvedEntity] = Field(default_factory=list)
    mention_to_entity: dict[str, str] = Field(default_factory=dict)
