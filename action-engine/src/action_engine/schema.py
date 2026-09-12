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


class CheckItem(BaseModel):
    """제출 준비물 하나. '미보유'와 '확보불가'는 다른 정보다 — 후자는 다른 경로를 안내해야 한다."""

    label: str
    required: bool = False
    state: str = "미보유"  # 보유 / 미보유 / 생성가능 / 확보불가
    reason: str | None = None
    doc_ids: list[str] = Field(default_factory=list, description="이 항목을 채운 자료함 문서")


class Checklist(BaseModel):
    """5단계 대조 결과.

    ``unresolved`` 가 차 있으면 사전에 필요 서류가 없다는 뜻이고, 화면은 아무것도 그리지 않는다.
    """

    action: str | None = None
    items: list[CheckItem] = Field(default_factory=list)
    done: int = 0
    total: int = 0
    unresolved: str | None = None


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


class CaseCardOut(BaseModel):
    """화면이 읽는 최종 카드.

    research-engine 의 ``CaseCard`` 를 그대로 담고 기능 2가 판정한 값을 덧붙인다.
    화면은 이 객체 하나만 읽으면 된다 — research-engine 출력을 따로 뒤지지 않는다.

        research-engine  ──CaseCard + ActionTrigger[]──▶  action-engine  ──CaseCardOut──▶  화면

    앞쪽 필드는 research-engine 이 만든 값을 손대지 않고 통과시킨다. 기능 2가 채운 것은
    ``st`` 아래부터다.
    """

    # ── research-engine CaseCard 통과 ──
    case_type: str
    case_type_label: str
    requirements_status: str = Field(description="draft_unverified 면 화면에 '검수 전' 표시")
    stages: list[dict] = Field(default_factory=list)
    current_stage: str | None = None
    evidence_doc_count: int = 0
    needs_confirmation_count: int = 0
    slots_done: int = 0
    slots_total: int = 0
    source_trigger: dict | None = Field(default=None, description="research-engine 이 고른 next_trigger 원본")

    # ── action-engine 이 채운 값 ──
    st: CodeHit
    inf: list[CodeHit] = Field(default_factory=list)
    tim: list[Deadline] = Field(default_factory=list)
    next_action: RuleHit | None = Field(default=None, description="우선순위 규칙이 고른 하나")
    also: list[RuleHit] = Field(default_factory=list, description="참고사항")
    checklist: Checklist | None = Field(default=None, description="5단계 대조 — 제출 준비물")
    procedure: None = Field(default=None, description="절차 문구 자리. 지식베이스가 붙기 전까지 항상 None")
