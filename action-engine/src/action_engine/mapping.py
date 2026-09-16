"""research-engine 출력 → ST · INF · TIM 코드 (A안 변환 계층).

두 코드 체계가 다르다.

    research-engine   Stage 6종(발생·송금·신고·접수·수사·결과) + GapCondition 12종
    여기              ST 12종 + INF 10종 + TIM 7종

research-engine 은 "결과 단계"까지만 알고 그게 불송치인지 수사중지인지는 구분하지 않는다.
대신 ``decision_type`` 슬롯에 결정 내용을 문자열로 뽑아 준다("수사중지", "불송치" 등).
ST 판정은 그 값을 우선순위 표에 넣어 내린다.

친구 코드는 건드리지 않는다. 변환은 전부 이 파일 안에서 끝난다.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .codes import INF, ST, label
from .schema import CaseState, CodeHit, Confidence

# ── ST 판정표 ───────────────────────────────────────────────────────────
# 위에서부터 먼저 맞는 하나. decision_type 값에 needles 중 하나가 들어 있으면 채택하되,
# excludes 중 하나라도 들어 있으면 건너뛴다.
#
# excludes 가 필요한 이유: '불기소' 안에 '기소'가 들어 있다. 부분 문자열만 보면
# 불기소(ST-302)를 재판 진행 중(ST-401)으로 판정한다 — 정반대 결론이다.
# 같은 이유로 '불송치(혐의없음)' 도 걸러야 한다. 혐의없음은 불송치의 '이유'이지
# 검찰의 불기소 처분이 아니다 — 통지서에 그렇게 적혀 온다. 잘못 보면 경찰에 낼
# 이의신청 대신 검찰 항고를 안내하게 되고, 실제로 열려 있는 불복 경로를 놓친다.
# 표 자체가 판정 근거이므로 조건을 코드가 아니라 데이터로 적는다.
DECISION_TABLE: list[tuple[tuple[str, ...], tuple[str, ...], ST, Confidence]] = [
    (("재심",), (), ST.RETRIAL_PREP, Confidence.CONFIRMED),
    (("확정판결", "판결확정"), (), ST.JUDGMENT_FINAL, Confidence.CONFIRMED),
    (("공소제기", "구공판", "구약식", "기소"), ("불기소",), ST.TRIAL_ONGOING, Confidence.CONFIRMED),
    (("재정신청",), (), ST.ADJUDICATION_REQUEST, Confidence.CONFIRMED),
    (("항고", "이의신청"), (), ST.APPEAL_PENDING, Confidence.CONFIRMED),
    (("불기소", "혐의없음", "공소권없음", "죄가안됨"), ("불송치",), ST.PROSECUTION_NO_CHARGE, Confidence.CONFIRMED),
    (("불송치",), (), ST.POLICE_NO_REFERRAL, Confidence.CONFIRMED),
    # 통지서에 "수사중지"로만 적히기도 하고 사유를 붙여 "참고인중지"로 적히기도 한다.
    # 사유(피의자·참고인)는 아래에서 다시 갈라 ST-201 / ST-202 를 정한다.
    (("수사중지", "수사 중지", "피의자중지", "참고인중지"), (), ST.SUSPENDED_SUSPECT, Confidence.CONFIRMED),
]

# 결정 내용이 없을 때 현재 단계로 추정한다 (전부 '추정').
STAGE_FALLBACK: dict[str, ST] = {
    "outcome": ST.UNKNOWN,  # 결과 단계인데 결정 내용이 없으면 물어봐야 한다
    "investigation": ST.POLICE_INVESTIGATING,
    "receipt": ST.POLICE_INVESTIGATING,
    "report": ST.PRE_INVESTIGATION,
    "transfer": ST.PRE_INVESTIGATION,
    "occurrence": ST.PRE_INVESTIGATION,
}

# ── INF 판정 ────────────────────────────────────────────────────────────
# research-engine 의 GapCondition → 우리 INF. 근거가 명확한 것만 옮긴다.
CONDITION_TO_INF: dict[str, INF] = {
    "conflicting": INF.CONTRADICTION_ACROSS,  # 화자가 같으면 아래에서 INF-023 으로 바꾼다
    "suspected_conflict": INF.CONTRADICTION_ACROSS,
    "time_gap": INF.RECORD_GAP,
    "stage_skipped": INF.RECORD_GAP,
    "claimed_only": INF.SOURCE_MISSING,
    "low_confidence": INF.SOURCE_MISSING,
    "unreadable": INF.SOURCE_MISSING,
    "missing": INF.SOURCE_MISSING,
    "stage_stalled": INF.RECORD_UNCHECKED,
    "possibly_outdated": INF.RECORD_UNCHECKED,
    "unrecorded_fact": INF.RECORD_UNCHECKED,
    # identity_unconfirmed 는 대응하는 INF 코드가 없다. 옮기지 않는다.
}

# 자료 종류 → 신규 정보 유입(INF-01*). 파일 종류만 보면 정해지므로 규칙으로 판정한다.
DOCTYPE_TO_INF: dict[str, INF] = {
    "statement": INF.NEW_STATEMENT,
    "memo": INF.NEW_STATEMENT,
    "complaint": INF.NEW_STATEMENT,
    "messenger": INF.NEW_PHYSICAL,
    "receipt": INF.NEW_PHYSICAL,
    "forensic": INF.NEW_FORENSIC,
    "news": INF.NEW_MEDIA,
    # notice·user_note 는 신규 정보가 아니라 절차 기록·사용자 입력이라 뺀다.
}


def _slot_map(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["slot"]: s for s in result.get("analysis", {}).get("slot_statuses", [])}


def _parse_date(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v)[:10]).date()
    except ValueError:
        return None


def st_from_decision(value: str, doc_ids: list[str] | None = None, *, confirmed: bool = True) -> CodeHit | None:
    """결정 내용 한 줄 → ST 하나. 표에 없는 말이면 None (지어내지 않는다).

    자료에서 읽은 결정과 사용자가 '이런 답을 받았다'고 적은 결정을 같은 표로 판정한다.
    판정 근거가 두 벌이 되면 화면과 엔진이 다른 말을 하게 된다.
    ``confirmed`` 가 False 면 확정으로 올리지 않는다 — 기록이 흔들리거나 사용자의 말일 때다.
    """
    value = (value or "").strip()
    if not value:
        return None
    doc_ids = doc_ids or []

    for needles, excludes, code, conf in DECISION_TABLE:
        if any(x in value for x in excludes):
            continue
        if not any(n in value for n in needles):
            continue
        # 수사중지는 사유(피의자/참고인)까지 봐야 201·202 가 갈린다.
        if code is ST.SUSPENDED_SUSPECT:
            if "참고인" in value:
                code = ST.SUSPENDED_WITNESS
            elif "피의자" not in value:
                return CodeHit(
                    code=ST.SUSPENDED_SUSPECT, label=label(ST.SUSPENDED_SUSPECT),
                    confidence=Confidence.PRESUMED,
                    reason=f"결정 내용이 '{value}' 로 확인되었으나 피의자중지·참고인중지 구분이 없습니다",
                    source_doc_ids=doc_ids,
                    ambiguous_between=[ST.SUSPENDED_SUSPECT, ST.SUSPENDED_WITNESS],
                )
        return CodeHit(
            code=code, label=label(code),
            confidence=conf if confirmed else Confidence.PRESUMED,
            reason=f"결정 내용이 '{value}' 로 확인되었습니다",
            source_doc_ids=doc_ids,
        )
    return None


def resolve_st(result: dict[str, Any]) -> CodeHit:
    """D1 — 절차 단계 판정. 상호배타이므로 하나만 돌려준다."""
    slots = _slot_map(result)
    decision = slots.get("decision_type") or {}
    value = (decision.get("value") or "").strip()
    doc_ids = [s["source_doc_id"] for s in decision.get("sources", [])]

    hit = st_from_decision(value, doc_ids, confirmed=decision.get("state") == "confirmed")
    if hit:
        return hit

    stage = result.get("timeline", {}).get("current_stage")
    fallback = STAGE_FALLBACK.get(stage, ST.UNKNOWN)
    if fallback is ST.UNKNOWN:
        return CodeHit(
            code=ST.UNKNOWN, label=label(ST.UNKNOWN), confidence=Confidence.UNDETERMINED,
            reason="결정 내용을 자료에서 찾지 못했습니다. 받으신 통지서를 확인해야 합니다",
        )
    return CodeHit(
        code=fallback, label=label(fallback), confidence=Confidence.PRESUMED,
        reason=f"결정 내용은 없지만 현재 단계가 '{stage}' 라 추정했습니다",
    )


def resolve_inf(result: dict[str, Any]) -> list[CodeHit]:
    """D2 — 정보 결합 상태. 여러 개가 동시에 참일 수 있으므로 전부 모은다."""
    hits: dict[str, CodeHit] = {}
    analysis = result.get("analysis", {})

    def add(code: str, reason: str, key: str | None = None, doc_ids: list[str] | None = None,
            conf: Confidence = Confidence.CONFIRMED) -> None:
        hit = hits.get(code)
        if hit is None:
            hits[code] = CodeHit(code=code, label=label(code), confidence=conf, reason=reason,
                                 source_trigger_keys=[key] if key else [],
                                 source_doc_ids=list(doc_ids or []))
            return
        if key and key not in hit.source_trigger_keys:
            hit.source_trigger_keys.append(key)
        for d in doc_ids or []:
            if d not in hit.source_doc_ids:
                hit.source_doc_ids.append(d)

    # 1) 신규 정보 유입(INF-01*)
    #
    # "자료가 있다"가 아니라 "기록에 반영되지 않은 자료가 있다"여야 한다.
    # 자료함에 문서가 있다는 것만으로 켜면 INF-01 이 항상 참이 되어 우선순위 표가 무의미해진다.
    # research-engine 의 unrecorded_fact 가 바로 그 판정("이 사실이 기록 자료에서 확인되지 않는다")을
    # 해 주므로, 그 근거가 된 문서의 종류로 INF-01* 를 가른다.
    docs_by_id = {d.get("doc_id"): d for d in result.get("documents", [])}
    for issue in analysis.get("issues", []):
        if issue.get("condition") != "unrecorded_fact":
            continue
        key = (issue.get("trigger") or {}).get("key")
        for ref in issue.get("sources", []):
            doc = docs_by_id.get(ref.get("source_doc_id")) or {}
            code = DOCTYPE_TO_INF.get(doc.get("doc_type"))
            if code:
                add(code, f"{doc.get('file_name') or doc.get('doc_id')} 의 내용이 기록 자료에서 확인되지 않습니다",
                    key=key, doc_ids=[doc.get("doc_id")])

    # 2) 모순·공백·근거미비 → issue 의 condition 으로 판정
    speakers = {c["claim_id"]: c.get("speaker") for c in result.get("extraction", {}).get("claims", [])}
    for issue in analysis.get("issues", []):
        cond = issue.get("condition")
        code = CONDITION_TO_INF.get(cond)
        if code is None:
            continue
        # 같은 화자의 진술이 엇갈리면 INF-023
        if cond == "conflicting" and _same_speaker(issue, speakers):
            code = INF.CONTRADICTION_SELF
        conf = Confidence.PRESUMED if cond == "suspected_conflict" else Confidence.CONFIRMED
        add(code, issue.get("message", ""), key=(issue.get("trigger") or {}).get("key"),
            doc_ids=[s["source_doc_id"] for s in issue.get("sources", [])], conf=conf)

    # 3) 감정 자료가 없으면 전문 분석 미실시
    if not any(d.get("doc_type") == "forensic" for d in result.get("documents", [])):
        add(INF.ANALYSIS_NOT_DONE, "감정 결과 자료가 자료함에 없습니다")

    return sorted(hits.values(), key=lambda h: h.code)


def inf_from_triggers(triggers: list[dict[str, Any]]) -> list[CodeHit]:
    """``action_triggers[]`` 만으로 INF 를 판정한다 — research-engine 이 선언한 연동 계약.

    ``ActionTrigger`` 에는 판정에 필요한 것이 다 들어 있다(``condition`` · ``stage`` · ``slot``
    · ``since`` · ``elapsed_days`` · ``evidence``). issues[] 전체를 뒤지지 않아도 된다.

    다만 트리거에는 사람이 읽을 메시지와 화자 정보가 없다. 그래서
    - 근거 문장은 트리거 키로 대신한다
    - 모순은 화자를 알 수 없으므로 INF-021 로만 둔다 (INF-023 으로 올리지 않는다)

    화면에 보여줄 문장까지 필요하면 ``resolve_inf`` 를 쓴다.
    """
    hits: dict[str, CodeHit] = {}
    for t in triggers:
        code = CONDITION_TO_INF.get(t.get("condition"))
        if code is None:
            continue
        hit = hits.get(code)
        if hit is None:
            hits[code] = CodeHit(
                code=code, label=label(code),
                reason=f"{t.get('condition')} 트리거가 발생했습니다",
                source_trigger_keys=[t["key"]],
                source_doc_ids=[e["source_doc_id"] for e in t.get("evidence", [])],
            )
        elif t["key"] not in hit.source_trigger_keys:
            hit.source_trigger_keys.append(t["key"])
    return sorted(hits.values(), key=lambda h: h.code)


def basis_from_triggers(triggers: list[dict[str, Any]]) -> dict[str, date | None]:
    """트리거의 ``since`` 로 기한 기산일을 채운다 — '기한 계산용'이라고 선언된 필드다."""
    out: dict[str, date | None] = {}
    for t in triggers:
        since = _parse_date(t.get("since"))
        if since is None:
            continue
        # 결정 이후 진행이 멈춘 트리거의 since 가 곧 결정 통지 시점이다
        if t.get("condition") == "stage_stalled" and "decision_time" not in out:
            out["decision_time"] = since
    return out


def _same_speaker(issue: dict[str, Any], speakers: dict[str, str | None]) -> bool:
    """모순 난 두 진술이 같은 사람 것인지 — INF-021(진술 간) 과 INF-023(동일인 번복) 을 가른다.

    PairDecision 에는 화자 필드가 없다. 대신 Claim 에 ``speaker`` 가 있으므로
    모순 쌍의 claim_id 두 개를 찾아 화자를 비교한다.
    화자를 못 찾으면 False — 억지로 INF-023 으로 올리지 않고 INF-021 로 둔다.
    """
    decision = issue.get("decision") or {}
    a = speakers.get(decision.get("claim_a_id"))
    b = speakers.get(decision.get("claim_b_id"))
    return bool(a and b and a == b)


def to_case_state(result: dict[str, Any]) -> CaseState:
    """research-engine 출력 dict 하나를 29개 코드 체계로 옮긴다. TIM 은 rules 단계에서 채운다."""
    return CaseState(
        case_id=result.get("case_id", ""),
        case_type=result.get("case_type", ""),
        as_of=_parse_date(result.get("as_of")) or date.today(),
        st=resolve_st(result),
        inf=resolve_inf(result),
        tim=[],
    )
