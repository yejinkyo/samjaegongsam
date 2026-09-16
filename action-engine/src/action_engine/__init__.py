"""다음 행동 강령 엔진 (기능 2 백엔드).

research-engine(기능 1) 이 "무엇이 비어 있는가"까지 하고 멈춘다.
이 패키지는 그 출력을 29개 상태 코드로 옮기고, 우선순위 규칙으로 다음 행동을 고른다.

절차(무엇을·어디에·어떻게·언제까지)는 만들지 않는다 — 검증된 지식베이스의 몫이다.
"""

from .agencies import describe_submit_to, find_agency, find_parent, load_agencies
from .checklist import build_checklist, load_documents
from .codes import EXCLUDED, INF, LABELS, ST, TIM, label
from .limitation import compute_limitation, find_offence, load_offences
from .mapping import basis_from_triggers, inf_from_triggers, resolve_inf, resolve_st, to_case_state
from .rules import build_card, compute_deadlines, decide, run
from .schema import (
    ActionDecision,
    CaseCardOut,
    CaseState,
    CheckItem,
    Checklist,
    CodeHit,
    Confidence,
    Deadline,
    RuleHit,
    Submission,
    SubmissionResponse,
)
from .submissions import status_of, waiting_days

__all__ = [
    "ST", "INF", "TIM", "LABELS", "EXCLUDED", "label",
    "CaseState", "CodeHit", "Confidence", "Deadline", "RuleHit", "ActionDecision", "CaseCardOut", "CheckItem", "Checklist",
    "Submission", "SubmissionResponse", "status_of", "waiting_days",
    "to_case_state", "resolve_st", "resolve_inf", "inf_from_triggers", "basis_from_triggers",
    "compute_deadlines", "decide", "run", "build_card", "build_checklist", "load_documents",
    "compute_limitation", "find_offence", "load_offences",
    "find_agency", "find_parent", "describe_submit_to", "load_agencies",
]
