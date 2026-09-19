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
    issuer: str | None = Field(
        default=None,
        description="결정을 낸 기관 — police(경찰) · prosecution(검찰). 기한·불복 서류가 기관에 따라 갈린다. 모르면 None",
    )


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
    advisory: str | None = Field(default=None, description="기한은 없지만 알려줄 것")
    submit_to: str | None = Field(default=None, description="제출처. 지식베이스에서만 온다")


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
    ``no_submission`` 은 다르다 — 서류를 못 채운 게 아니라 **제출할 서류가 없는 단계**라는 정보다.
    기한의 '법정 기한 없음'과 '아직 못 채움'을 가르는 것과 같은 이유다.
    """

    action: str | None = None
    items: list[CheckItem] = Field(default_factory=list)
    done: int = 0
    total: int = 0
    unresolved: str | None = None
    no_submission: str | None = Field(default=None, description="제출 절차가 아닌 단계일 때 그 이유")
    # 아래는 전부 지식베이스에서만 온다. 없으면 화면은 빈칸으로 둔다.
    form_name: str | None = Field(default=None, description="제출할 서류의 정식 명칭")
    form_source: str | None = Field(default=None, description="서식의 근거 (예: 경찰수사규칙 별지 제125호 서식)")
    form_url: str | None = Field(default=None, description="공식 서식 내려받기 주소")
    submit_to: str | None = Field(default=None, description="제출처")
    statute: str | None = Field(default=None, description="근거 법령")
    prerequisite: str | None = Field(default=None, description="먼저 거쳐야 하는 절차")
    source: str | None = Field(default=None, description="확인한 공식 출처 주소")
    advisory: str | None = Field(default=None, description="서류 외에 함께 알려줄 것")
    reason_heading: str | None = Field(default=None, description="초안에서 사용자가 직접 쓰는 칸의 제목. 없으면 '이의 사유'")
    reason_note: str | None = Field(default=None, description="그 칸에 붙이는 안내")


class SubmissionResponse(BaseModel):
    """제출에 대해 받은 답."""

    received_at: date
    doc_id: str | None = Field(default=None, description="회신 통지서 문서 id. 없으면 받았다는 말뿐이다")
    decision_type: str | None = Field(
        default=None,
        description="결정 내용. DECISION_TABLE 에 있는 말만 뜻이 있고, 없는 말은 판정에 쓰지 않는다",
    )


class Submission(BaseModel):
    """무엇을 언제 어디에 냈고 어떤 답을 받았는가.

    이걸 모르면 엔진은 이미 낸 절차를 계속 다음 행동으로 띄우고, '냈는데 답이 없다'는
    사실을 셀 자리가 없다. 장기 미제 사건에서 그 사실 자체가 다음 행동의 근거다.

    여기에 법적 판단은 없다 — 날짜와 '자료가 남아 있느냐'만 담는다.
    """

    submission_id: str
    action: str = Field(description="어느 행동을 냈는지. RuleHit.action 과 같은 키")
    submitted_at: date
    planned_due: date | None = Field(default=None, description="낼 당시의 기한. 없으면 null")
    submitted_to: str | None = Field(default=None, description="제출처. 지식베이스 값을 그대로 옮긴다")
    evidence_doc_id: str | None = Field(default=None, description="접수증 문서 id. 없으면 낸 사실이 본인 말뿐이다")
    response: SubmissionResponse | None = None


class Citation(BaseModel):
    """문장 하나가 어느 자료 몇 줄에서 왔는지. 이게 없는 문장은 초안에 넣지 않는다."""

    doc_id: str
    file_name: str | None = None
    page: int | None = None
    line: int | None = None
    quote: str | None = None


class DraftLine(BaseModel):
    """사건 경위 한 줄.

    문장을 새로 짓지 않는다. 자료에 있는 날짜와 문구를 그대로 옮기고 출처를 단다.
    ``evidence_level`` 은 섞으면 안 되는 두 가지다 — 기록에서 온 것과 사람의 말에서 온 것.
    """

    date: str | None = None
    text: str
    evidence_level: str = "record"   # record / statement
    citations: list[Citation] = Field(default_factory=list)


class DraftField(BaseModel):
    """서식의 빈칸 하나. 채웠으면 어디서 왔는지, 못 채웠으면 왜인지 남긴다."""

    key: str
    label: str
    value: str | None = None
    filled_from: str | None = Field(default=None, description="knowledge_base / case_record")
    reason: str | None = Field(default=None, description="못 채운 이유. 값이 없을 때만 찬다")


class DraftSection(BaseModel):
    heading: str
    lines: list[DraftLine] = Field(default_factory=list)
    note: str | None = None


class DraftDocument(BaseModel):
    """낼 서류의 초안.

    ``is_draft`` 는 끄지 않는다. 사람이 읽고 고치기 전에는 제출용이 아니다.
    """

    action: str
    is_draft: bool = True
    form_name: str | None = None
    form_source: str | None = None
    form_url: str | None = None
    submit_to: str | None = None
    statute: str | None = None
    fields: list[DraftField] = Field(default_factory=list)
    unfilled: list[DraftField] = Field(default_factory=list)
    sections: list[DraftSection] = Field(default_factory=list)
    dropped: int = Field(default=0, description="출처가 없어 넣지 않은 사건 수")


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
    submissions: list[Submission] = Field(default_factory=list, description="사용자가 냈다고 기록한 것")
    procedure: None = Field(default=None, description="절차 문구 자리. 지식베이스가 붙기 전까지 항상 None")
