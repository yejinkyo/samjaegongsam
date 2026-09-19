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
from .mapping import effective_issuer
from .schema import ActionDecision, CaseCardOut, CaseState, CodeHit, Deadline, RuleHit, Submission

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
    basis_notes: dict[str, str] | None = None,
) -> list[Deadline]:
    """D3 — 기한 산출.

    ``period_days`` 나 기산일이 없으면 D-day 를 만들지 않고 ``unresolved`` 에 이유를 적는다.
    지식베이스가 비어 있는 지금은 대부분 여기로 떨어지는 것이 정상이다.
    """
    basis = basis or {}
    basis_notes = basis_notes or {}
    out: list[Deadline] = []

    issuer = effective_issuer(state.st)
    for row in load_deadlines()["deadlines"]:
        applies = row["applies_to_st"]
        if "*" not in applies and state.st.code not in applies:
            continue
        # 재판 · 확정 · 재심 단계에는 수사 단계의 기한을 붙이지 않는다 — 이유는 행의 except_why
        if state.st.code in row.get("except_st", []):
            continue
        # 같은 단계라도 결정한 기관에 따라 불복 절차가 다르다 — 경찰 수사중지는 이의제기, 검사의 기소중지는 항고
        if row.get("issuer") and row["issuer"] != issuer:
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
                if basis_notes.get("incident_end"):
                    d.advisory += " " + basis_notes["incident_end"]
            out.append(d)
            continue

        missing = [k for k in row.get("requires", []) if k != "죄명"]
        if missing:
            d.unresolved = f"{', '.join(missing)} 정보가 없어 계산할 수 없습니다"
            out.append(d)
            continue

        d.basis_date = basis.get(row.get("basis"))
        d.advisory = basis_notes.get(row.get("basis"))
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
            if rule.get("stop"):
                # 이 줄이 맞으면 뒤의 규칙은 보지 않는다 — 재판 단계에 '수사기관에 제출'이 참고사항으로 뜨면 안 된다
                break

    return ActionDecision(main=hits[0] if hits else None, also=hits[1:], state=state)


# 범행이 끝난 때를 가리키는 항목. 앞의 것이 사건 유형에 더 맞는 값이다 —
# 실종은 마지막으로 목격된 때, 사기는 돈을 보낸 때, 그 밖에는 사건이 일어난 때.
INCIDENT_END_SLOTS = ("last_seen_time", "transfer_time", "incident_time")


def incident_end_basis(result: dict[str, Any]) -> tuple[date | None, str | None]:
    """공소시효의 기산일(범행 종료일)과, 추정한 값이면 그 사실을 알리는 문장.

    기록으로 확인된 항목 값을 먼저 쓴다. 없으면 진술 · 메모에 적힌 같은 항목의 날짜 가운데
    **가장 이른 날**을 쓴다 — 늦은 날로 계산하면 이미 끝난 시효를 '아직 남았다'고 안내하게 된다.
    화면에 직접 적은 메모는 쓰지 않는다.
    """
    from .mapping import _parse_date, _slot_map

    slots = _slot_map(result)
    for name in INCIDENT_END_SLOTS:
        slot = slots.get(name) or {}
        if slot.get("state") == "confirmed" and (when := _parse_date(slot.get("value"))):
            return when, None
    for name in INCIDENT_END_SLOTS:
        said = [
            when for c in result.get("extraction", {}).get("claims", [])
            if c.get("slot") == name and c.get("evidence_level") != "user"
            and (when := _parse_date((c.get("slot_time") or {}).get("start")))
        ]
        if said:
            first = min(said)
            return first, (f"범행 종료일이 기록으로 확인되지 않아, 진술에 적힌 가장 이른 날({first:%Y-%m-%d})을 "
                           "기준으로 계산했습니다. 실제 범행이 더 늦게 끝났다면 시효도 그만큼 늦게 끝납니다.")
    return None, None


def communication_dates(result: dict[str, Any]) -> list[tuple[date, str]]:
    """통신이 오간 날(통신사실확인자료가 생긴 날)과 그 출처.

    메신저 대화의 메시지 시각과 '마지막 연락' 시점이다. 화면에 직접 적은 메모는 쓰지 않는다 —
    사업자에게 보존을 요청할 때 근거로 내밀 수 있는 자료가 아니다.
    """
    from .mapping import _parse_date

    types = {d["doc_id"]: d.get("doc_type") for d in result.get("documents", [])}
    names = {d["doc_id"]: d.get("file_name") or d["doc_id"] for d in result.get("documents", [])}
    out: set[tuple[date, str]] = set()
    for c in result.get("extraction", {}).get("claims", []):
        if c.get("evidence_level") == "user":
            continue
        if types.get(c["doc_id"]) == "messenger" and (when := _parse_date((c.get("said_at") or {}).get("start"))):
            out.add((when, f"{names[c['doc_id']]}의 메신저 대화"))
        if c.get("slot") == "last_contact_time" and (when := _parse_date((c.get("slot_time") or {}).get("start"))):
            out.add((when, f"{names.get(c['doc_id'], c['doc_id'])}에 적힌 마지막 연락"))
    return sorted(out)


def retention_basis(dates: list[tuple[date, str]], period_days: int, as_of: date) -> tuple[date, str]:
    """보존 기한을 어느 날부터 셀지 — **다음으로 사라질 기록**의 통신일.

    통신 기록은 날마다 따로 사라진다. 이미 사라진 날을 기준으로 삼으면 남은 기록까지 없는 것으로
    안내하고, 가장 늦은 날을 기준으로 삼으면 곧 사라질 기록을 놓친다. 그래서 아직 남은 기록 가운데
    가장 먼저 사라질 날을 쓴다. 전부 지났으면 가장 늦은 날(이미 만료)을 쓴다.
    """
    alive = [(d, why) for d, why in dates if d + timedelta(days=period_days) >= as_of]
    when, why = alive[0] if alive else dates[-1]
    note = f"기산일은 {why}({when:%Y-%m-%d})입니다."
    last, last_why = dates[-1]
    if last != when:
        note += (f" 가장 늦은 통신은 {last_why}({last:%Y-%m-%d})로, 그 기록은 "
                 f"{last + timedelta(days=period_days):%Y-%m-%d}까지 남습니다.")
    gone = [d for d, _ in dates if d + timedelta(days=period_days) < as_of]
    if gone and alive:
        note += f" 그보다 앞선 통신 {len(gone)}건은 이미 보존 기간이 지났습니다."
    return when, note


def run(result: dict[str, Any], st_override: CodeHit | None = None,
        decision_time: date | None = None) -> ActionDecision:
    """research-engine 출력 dict → 다음 행동 판정. 이 패키지의 입구.

    ``st_override`` · ``decision_time`` 은 사용자가 '이런 답을 받았다'고 기록했을 때 쓴다.
    기한표는 단계(``applies_to_st``)와 통지 수령일로 갈리므로, 단계만 바꾸고 기한을 그대로
    두면 새 단계에 없는 기한이 남는다. 둘을 같이 갈아 끼우고 규칙을 다시 돌린다.
    """
    from .mapping import _parse_date, _slot_map, basis_from_triggers, to_case_state

    state = to_case_state(result)
    if st_override:
        state.st = st_override
    slots = _slot_map(result)
    # 슬롯에서 먼저 찾고, 없으면 트리거의 since 로 메운다
    basis: dict[str, date | None] = {
        **basis_from_triggers(result.get("analysis", {}).get("action_triggers", [])),
    }
    basis.setdefault("decision_time", _parse_date((slots.get("decision_time") or {}).get("value")))
    incident_end, incident_note = incident_end_basis(result)
    basis.setdefault("incident_end", incident_end)
    notes: dict[str, str] = {}
    period = next((r["period_days"] for r in load_deadlines()["deadlines"] if r["code"] == "TIM-031"), None)
    if (comms := communication_dates(result)) and period:
        basis["communication_time"], notes["communication_time"] = retention_basis(comms, period, state.as_of)
    if decision_time:
        basis["decision_time"] = decision_time
    # 죄명은 research-engine 의 offence 슬롯 — 통지서마다 다르면 가장 최근 통지서의 죄명이다
    offence = (slots.get("offence") or {}).get("value")
    if incident_note:
        notes["incident_end"] = incident_note
    state.tim = compute_deadlines(state, basis, offence=offence, basis_notes=notes)
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
    from .submissions import st_from_responses

    decision = run(result)

    # 받은 답을 기록했으면 사건 단계를 그 답으로 다시 보고 규칙을 다시 돌린다.
    # 이게 이 기능의 핵심이다 — 답이 무엇이었느냐에 따라 다음에 할 일이 달라진다.
    from .submissions import latest_answer

    answered_st = st_from_responses(submissions or [])
    answered = latest_answer(submissions or [])
    if answered_st and answered and answered_st.code != decision.state.st.code:
        decision = run(result, st_override=answered_st, decision_time=answered.response.received_at)
    card = result.get("analysis", {}).get("case_card", {}) or {}
    checklist = build_checklist(
        decision.main.action if decision.main else None,
        result.get("documents", []),
        decision.state.tim,
        st=decision.state.st.code,
        issuer=effective_issuer(decision.state.st),
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
