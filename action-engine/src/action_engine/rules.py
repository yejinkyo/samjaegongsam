"""DMN 우선순위 평가기 + TIM 기한 계산.

조합표(if-else 전부 나열)나 가중치를 쓰지 않는다. 경우의 수는 ST 12 × INF 2^10 × TIM 2^7
= 1,572,864 개라 나열이 불가능하다. 대신 우선순위 규칙 10줄로 덮는다.

평가기가 하는 일은 셋뿐이다.
1. 규칙을 순서대로 훑어 ``when`` 의 모든 칸이 맞는지 본다
2. 먼저 맞는 하나를 메인, 나머지를 참고사항으로 모은다
3. 발화한 규칙 번호를 결과에 같이 실어 보낸다  ← 설명 가능성의 전부
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from .codes import label
from .schema import ActionDecision, CaseCardOut, CaseState, Deadline, RuleHit, Submission

DATA = Path(__file__).parent / "data"

CRITICAL_DAYS = 7
SOON_DAYS = 30


@lru_cache(maxsize=1)
def load_rules() -> dict[str, Any]:
    return json.loads((DATA / "rules.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_deadlines() -> dict[str, Any]:
    return json.loads((DATA / "deadlines.json").read_text(encoding="utf-8"))


def _severity(days_left: int | None) -> str:
    if days_left is None:
        return "unknown"
    if days_left < 0:
        return "expired"
    if days_left <= CRITICAL_DAYS:
        return "critical"
    if days_left <= SOON_DAYS:
        return "soon"
    return "ok"


def compute_deadlines(
    state: CaseState,
    basis: dict[str, date | None] | None = None,
    offence: str | None = None,
) -> list[Deadline]:
    """D3 — 기한 산출.

    ``period_days`` 나 기산일이 없으면 D-day 를 만들지 않고 ``unresolved`` 에 이유를 적는다.
    지식베이스가 비어 있는 지금은 대부분 여기로 떨어지는 것이 정상이다.
    """
    basis = basis or {}
    out: list[Deadline] = []

    for row in load_deadlines()["deadlines"]:
        applies = row["applies_to_st"]
        if "*" not in applies and state.st.code not in applies:
            continue

        code = row["code"]
        d = Deadline(code=code, label=label(code), basis_reason=row.get("basis_label"),
                     statute=row.get("statute"), submit_to=row.get("submit_to"))

        # 기한이 아예 없는 절차. "아직 못 채웠다"와 구별해야 한다 —
        # 사용자에게는 "기한 제한이 없습니다"가 그 자체로 필요한 정보다.
        if row.get("unlimited") or row.get("no_statutory_limit"):
            d.severity = "ok"
            d.unresolved = None
            d.advisory = row.get("advisory")
            out.append(d)
            continue

        # 공소시효는 죄명 → 법정형 → 기간표를 거쳐야 해서 별도 계산기를 쓴다
        if code == "TIM-021":
            from .limitation import compute_limitation

            r = compute_limitation(offence, basis.get("incident_end"), state.as_of)
            if not r["resolved"]:
                d.unresolved = r["reason"]
            elif r.get("abolished"):
                d.severity = "ok"
                d.advisory = f"{r['offence']} — {r['note']}"
                d.statute = r.get("basis")
            else:
                d.basis_date = r["incident_end"]
                d.period_days = r["years"] * 365
                d.due_date = r["due_date"]
                d.days_left = r["days_left"]
                d.severity = _severity(r["days_left"])
                d.statute = r["statute"]
                d.advisory = f"{r['version_note']} ({r['years']}년). {r['caveat']}"
            out.append(d)
            continue

        missing = [k for k in row.get("requires", []) if k != "죄명"]
        if missing:
            d.unresolved = f"{', '.join(missing)} 정보가 없어 계산할 수 없습니다"
            out.append(d)
            continue

        d.basis_date = basis.get(row.get("basis"))
        if d.basis_date is None:
            d.unresolved = f"{row.get('basis_label')}을(를) 자료에서 찾지 못했습니다"
            out.append(d)
            continue

        if row.get("period_days") is None:
            d.unresolved = "기한이 지식베이스에 아직 없습니다 — 법령 확인 필요"
            out.append(d)
            continue

        d.period_days = row["period_days"]
        d.due_date = d.basis_date + timedelta(days=d.period_days)
        d.days_left = (d.due_date - state.as_of).days
        d.severity = _severity(d.days_left)
        out.append(d)

    return out


def _matches(when: dict[str, Any], state: CaseState) -> list[str]:
    """규칙 하나가 맞는지. 맞으면 근거가 된 코드 목록, 아니면 빈 목록.

    ``when`` 이 비어 있으면 항상 맞는다 (마지막 줄의 기본 행동).
    한 규칙 안의 조건들은 AND, 한 조건 안의 값들은 OR 다.
    """
    if not when:
        return []

    hit: list[str] = []

    if "st" in when:
        if state.st.code not in when["st"]:
            return []
        hit.append(state.st.code)

    if "inf" in when:
        codes = [h.code for h in state.inf if h.code in when["inf"]]
        if not codes:
            return []
        hit.extend(codes)

    if "tim_severity" in when:
        wanted_codes = when.get("tim_code")
        codes = [
            t.code for t in state.tim
            if t.severity in when["tim_severity"] and (not wanted_codes or t.code in wanted_codes)
        ]
        if not codes:
            return []
        hit.extend(codes)

    return hit


def decide(state: CaseState) -> ActionDecision:
    """D4 — 다음 행동. 먼저 맞는 하나가 메인, 나머지는 참고사항."""
    hits: list[RuleHit] = []

    for rule in load_rules()["rules"]:
        when = rule.get("when") or {}
        codes = _matches(when, state)
        if not when:
            # 기본 규칙은 다른 규칙이 하나도 안 맞았을 때만 쓴다
            if not hits:
                hits.append(RuleHit(rule_no=rule["no"], action=rule["action"],
                                    condition="기본", why=rule["why"], codes=[]))
            continue
        if codes:
            hits.append(RuleHit(rule_no=rule["no"], action=rule["action"],
                                condition=", ".join(f"{k}={v}" for k, v in when.items()),
                                why=rule["why"], codes=codes))

    return ActionDecision(main=hits[0] if hits else None, also=hits[1:], state=state)


def run(result: dict[str, Any]) -> ActionDecision:
    """research-engine 출력 dict → 다음 행동 판정. 이 패키지의 입구."""
    from .mapping import _parse_date, _slot_map, basis_from_triggers, to_case_state

    state = to_case_state(result)
    slots = _slot_map(result)
    # 슬롯에서 먼저 찾고, 없으면 트리거의 since 로 메운다
    basis: dict[str, date | None] = {
        **basis_from_triggers(result.get("analysis", {}).get("action_triggers", [])),
    }
    basis.setdefault("decision_time", _parse_date((slots.get("decision_time") or {}).get("value")))
    basis.setdefault("incident_end", _parse_date((slots.get("last_seen_time") or {}).get("value")))
    basis.setdefault("document_created", None)
    # 죄명은 research-engine 이 아직 뽑지 않는다. 슬롯에 생기면 여기서 넘어간다.
    offence = (slots.get("offence") or {}).get("value")
    state.tim = compute_deadlines(state, basis, offence=offence)
    return decide(state)


def build_card(result: dict[str, Any], submissions: list[Submission] | None = None) -> CaseCardOut:
    """화면이 읽을 카드 하나를 만든다.

    research-engine 의 ``CaseCard`` 를 통과시키고 기능 2가 판정한 값을 덧붙인다.
    화면은 이 함수의 결과만 읽으면 되고, research-engine 출력을 따로 뒤지지 않는다.

    ``submissions`` 는 사용자가 '냈다'고 기록한 것이다. 주면 이미 낸 행동을 다음 행동에서
    내리고 기다린 날수를 붙인다(:mod:`submissions`). 안 주면 지금까지와 똑같이 돈다.
    """
    from .checklist import build_checklist
    from .submissions import apply as apply_submissions

    decision = run(result)
    card = result.get("analysis", {}).get("case_card", {}) or {}
    checklist = build_checklist(
        decision.main.action if decision.main else None,
        result.get("documents", []),
        decision.state.tim,
        st=decision.state.st.code,
    )
    out = CaseCardOut(
        case_type=card.get("case_type", result.get("case_type", "")),
        case_type_label=card.get("case_type_label", ""),
        requirements_status=card.get("requirements_status", "unknown"),
        stages=card.get("stages", []),
        current_stage=card.get("current_stage"),
        evidence_doc_count=card.get("evidence_doc_count", 0),
        needs_confirmation_count=card.get("needs_confirmation_count", 0),
        slots_done=card.get("slots_done", 0),
        slots_total=card.get("slots_total", 0),
        source_trigger=card.get("next_trigger"),
        st=decision.state.st,
        inf=decision.state.inf,
        tim=decision.state.tim,
        next_action=decision.main,
        also=decision.also,
        checklist=checklist,
    )
    return apply_submissions(out, submissions or [], decision.state.as_of)
