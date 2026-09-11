"""입출력 모델.

research-engine 을 import 하지 않는다. 그쪽 출력 JSON(dict)만 받는다.
두 패키지를 따로 설치·테스트할 수 있고, 스키마가 바뀌어도 mapping.py 한 곳만 고치면 된다.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Confidence(StrEnum):
    CONFIRMED = "확정"  # 기록 자료로 확인됨
    PRESUMED = "추정"  # 정황으로 추론. 사용자 확인 필요
    UNDETERMINED = "미확정"  # 판정 불가 — 되물어야 한다


class CodeHit(BaseModel):
    """발화한 상태 코드 하나. 근거 없이는 만들지 않는다."""

    code: str
    label: str
    confidence: Confidence = Confidence.CONFIRMED
    reason: str = Field(description="왜 이 코드가 켜졌는지 한 줄")
    source_trigger_keys: list[str] = Field(default_factory=list, description="근거가 된 research-engine 트리거")
    source_doc_ids: list[str] = Field(default_factory=list)
    ambiguous_between: list[str] = Field(default_factory=list, description="둘 중 하나인데 자료로 못 가른 경우")


class Deadline(BaseModel):
    """TIM 하나의 기한 계산 결과.

    ``days_left`` 가 None 이면 계산에 필요한 값이 없다는 뜻이다 (기간이 지식베이스에 없거나
    기산일을 못 찾았거나). 그때는 화면에 D-day 를 만들어 내지 않는다.
    """

    code: str
    label: str
    basis_date: date | None = None
    basis_reason: str | None = None
    period_days: int | None = None
    due_date: date | None = None
    days_left: int | None = None
    severity: str = "unknown"  # expired / critical / soon / ok / unknown
    statute: str | None = Field(default=None, description="근거 법령. 지식베이스에서만 온다")
    unresolved: str | None = Field(default=None, description="계산을 막은 이유")


class CaseState(BaseModel):
    """29개 코드로 본 사건의 현재 상태."""

    case_id: str
    case_type: str
    as_of: date
    st: CodeHit
    inf: list[CodeHit] = Field(default_factory=list)
    tim: list[Deadline] = Field(default_factory=list)


class RuleHit(BaseModel):
    """발화한 우선순위 규칙. 설명 가능성의 핵심 — 화면이 이걸 그대로 인용한다."""

    rule_no: int
    action: str
    condition: str
    why: str
    codes: list[str] = Field(default_factory=list)


class ActionDecision(BaseModel):
    """다음 행동 판정 결과.

    절차(무엇을·어디에·어떻게·언제까지)는 여기 없다. ``action`` 은 지식베이스 조회 키일 뿐이고,
    문구는 검증된 지식베이스에서만 온다. 비어 있으면 화면은 빈칸으로 둔다.
    """

    main: RuleHit | None = None
    also: list[RuleHit] = Field(default_factory=list, description="동시에 맞은 나머지 규칙 (참고사항)")
    state: CaseState
    generated_at: datetime | None = None
