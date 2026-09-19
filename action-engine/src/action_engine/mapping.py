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

import re
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
#
# 장기·미제 사건 서류는 대부분 2021년 수사권 조정 전의 것이라 그때 말을 알아들어야 한다.
# - '기소중지'·'기소유예'에도 '기소'가 들어 있다. 재판 중(ST-401)으로 읽으면 멈춘 사건·끝난 사건을
#   재판 중이라고 안내한다. 기소중지는 피의자를 찾지 못해 수사를 멈춘 검사의 결정(ST-201),
#   기소유예는 불기소의 한 종류(ST-302)다
# - '송치'는 경찰이 사건을 검찰로 넘긴 것이다. '불기소의견 송치'도 검사가 아직 결정하지 않았으므로
#   불기소 줄보다 먼저 본다. '불송치' 안에도 '송치'가 들어 있어 뺀다
# - '무혐의'는 '혐의없음'을 흔히 이르는 말, '각하'는 불기소 주문의 하나다
# - '내사종결'(지금의 입건 전 조사 종결)은 입건되지 않고 끝난 것이라 입건 전 단계로 **추정**한다
DECISION_TABLE: list[tuple[tuple[str, ...], tuple[str, ...], ST, Confidence]] = [
    (("재심",), (), ST.RETRIAL_PREP, Confidence.CONFIRMED),
    (("확정판결", "판결확정"), (), ST.JUDGMENT_FINAL, Confidence.CONFIRMED),
    (("송치",), ("불송치",), ST.PROSECUTION_INVESTIGATING, Confidence.CONFIRMED),
    (("공소제기", "구공판", "구약식", "기소"), ("불기소", "기소중지", "기소유예"), ST.TRIAL_ONGOING, Confidence.CONFIRMED),
    (("재정신청",), (), ST.ADJUDICATION_REQUEST, Confidence.CONFIRMED),
    (("항고", "이의신청"), (), ST.APPEAL_PENDING, Confidence.CONFIRMED),
    (("불기소", "기소유예", "혐의없음", "무혐의", "공소권없음", "죄가안됨", "각하"), ("불송치",),
     ST.PROSECUTION_NO_CHARGE, Confidence.CONFIRMED),
    (("불송치",), (), ST.POLICE_NO_REFERRAL, Confidence.CONFIRMED),
    # 통지서에 "수사중지"로만 적히기도 하고 사유를 붙여 "참고인중지"로 적히기도 한다.
    # 사유(피의자·참고인)는 아래에서 다시 갈라 ST-201 / ST-202 를 정한다.
    (("수사중지", "수사 중지", "피의자중지", "참고인중지", "기소중지"), (), ST.SUSPENDED_SUSPECT, Confidence.CONFIRMED),
    (("내사종결", "내사 종결", "입건전조사 종결", "불입건"), (), ST.PRE_INVESTIGATION, Confidence.PRESUMED),
]

# ── 결정을 낸 기관 ──────────────────────────────────────────────────────
# 같은 말을 경찰과 검찰이 모두 쓰는 결정 사유. 경찰의 불송치(수사준칙 제51조제1항제3호)와 검사의
# 불기소(제52조제1항제2호)가 '혐의없음 · 죄가안됨 · 공소권없음 · 각하'를 함께 쓴다. 이 말만 있으면
# 불송치인지 불기소인지 모른다 — 틀리면 경찰에 낼 이의신청 대신 검찰 항고를 안내하게 된다.
SHARED_REASONS = ("혐의없음", "무혐의", "죄가안됨", "공소권없음", "각하")
# 한쪽 기관만 내리는 결정 — 결정 문구만으로 기관이 정해진다 (수사준칙 제51조 · 제52조)
PROSECUTION_ONLY = ("기소중지", "기소유예", "불기소", "공소제기", "구공판", "구약식")
POLICE_ONLY = ("수사중지", "불송치")
# 통지서 발급 기관 (research-engine 이 기록 자료의 화자로 넘겨준다: '**경찰서' · '**지방검찰청')
POLICE_ISSUER = re.compile(r"경찰서|경찰청|경찰관서")
PROSECUTION_ISSUER = re.compile(r"검찰청|지청")
# 수사권 조정 시행일. 그 전에는 경찰에 불송치·수사중지 결정 권한이 없어 수사 결정은 모두 검사가 했다
REFORM_DATE = date(2021, 1, 1)
# 결정 기관을 모를 때 단계만으로 정하는 기관. 중지는 조정 이후 흔한 경찰 결정을 기본으로 본다
DEFAULT_ISSUER: dict[str, str] = {
    ST.POLICE_NO_REFERRAL: "police",
    ST.SUSPENDED_SUSPECT: "police",
    ST.SUSPENDED_WITNESS: "police",
    ST.PROSECUTION_NO_CHARGE: "prosecution",
    ST.APPEAL_PENDING: "prosecution",
    ST.ADJUDICATION_REQUEST: "prosecution",
}


def effective_issuer(st: CodeHit) -> str | None:
    """기한·불복 서류를 고를 때 쓰는 기관. 자료로 가린 기관이 먼저고, 없으면 단계로 정한다."""
    return st.issuer or DEFAULT_ISSUER.get(st.code)


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
            elif "피의자" not in value and "기소중지" not in value:  # 기소중지는 피의자를 찾지 못해 멈춘 것
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


def _decision_date(result: dict[str, Any], decision: dict[str, Any]) -> date | None:
    """결정 시점: 결정일자 슬롯 → 결정을 적은 문서의 작성일."""
    when = _parse_date((_slot_map(result).get("decision_time") or {}).get("value"))
    if when:
        return when
    dates = (result.get("extraction") or {}).get("document_dates") or {}
    for src in decision.get("sources", []):
        value = (dates.get(src.get("source_doc_id")) or {}).get("value") or {}
        when = _parse_date(value.get("start"))
        if when:
            return when
    return None


def decision_issuer(result: dict[str, Any], decision: dict[str, Any], value: str) -> str | None:
    """결정을 낸 기관. 결정 문구 → 통지서 발급 기관 → 결정 시점(수사권 조정 전이면 검찰) 순."""
    if "송치" in value and "불송치" not in value:
        return "police"  # 검찰송치는 사법경찰관의 결정이다 (수사준칙 제51조제1항제2호)
    if any(word in value for word in PROSECUTION_ONLY):
        return "prosecution"
    if any(word in value for word in POLICE_ONLY):
        return "police"
    ids = set(decision.get("claim_ids") or [])
    speakers = [c.get("speaker") or "" for c in (result.get("extraction") or {}).get("claims", []) if c.get("claim_id") in ids]
    police = any(POLICE_ISSUER.search(s) for s in speakers)
    prosecution = any(PROSECUTION_ISSUER.search(s) for s in speakers)
    if police != prosecution:
        return "police" if police else "prosecution"
    when = _decision_date(result, decision)
    if when is not None and when < REFORM_DATE:
        return "prosecution"
    return None


def _only_shared_reason(value: str) -> bool:
    """'혐의없음'처럼 경찰·검찰이 함께 쓰는 사유만 있고 불송치·불기소를 밝히지 않았는가."""
    return any(w in value for w in SHARED_REASONS) and not any(w in value for w in ("불송치", "불기소", "기소유예"))


def resolve_st(result: dict[str, Any]) -> CodeHit:
    """D1 — 절차 단계 판정. 상호배타이므로 하나만 돌려준다."""
    slots = _slot_map(result)
    decision = slots.get("decision_type") or {}
    value = (decision.get("value") or "").strip()
    doc_ids = [s["source_doc_id"] for s in decision.get("sources", [])]

    hit = st_from_decision(value, doc_ids, confirmed=decision.get("state") == "confirmed")
    if hit:
        issuer = decision_issuer(result, decision, value)
        if _only_shared_reason(value):
            if issuer == "police":
                hit = CodeHit(
                    code=ST.POLICE_NO_REFERRAL, label=label(ST.POLICE_NO_REFERRAL), confidence=hit.confidence,
                    reason=f"결정 내용 '{value}' 가 경찰의 통지서에 적혀 있어 경찰 불송치로 봅니다",
                    source_doc_ids=doc_ids,
                )
            elif issuer is None:
                return CodeHit(
                    code=ST.UNKNOWN, label=label(ST.UNKNOWN), confidence=Confidence.UNDETERMINED,
                    reason=(f"결정 내용 '{value}' 은 경찰 불송치와 검찰 불기소에 모두 쓰는 말이라, "
                            "통지서를 낸 기관(경찰서 · 검찰청)을 알아야 단계를 정할 수 있습니다"),
                    source_doc_ids=doc_ids,
                    ambiguous_between=[ST.POLICE_NO_REFERRAL, ST.PROSECUTION_NO_CHARGE],
                )
        if issuer == "prosecution" and hit.code in (ST.SUSPENDED_SUSPECT, ST.SUSPENDED_WITNESS):
            # 검사의 기소중지 · 참고인중지는 불기소결정에 포함되어 항고 대상이다 (검찰사건사무규칙 제147조제1항)
            hit.reason += " — 검사의 결정이라 불복은 항고입니다"
        hit.issuer = issuer
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
    speakers = {c["claim_id"]: c for c in result.get("extraction", {}).get("claims", [])}
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


# 사람 하나를 가리키지 않는 화자 이름. research-engine 이 이름을 못 찾으면 역할이나 문서 종류로 적는다 —
# 두 기사가 모두 '보도', 두 진술서가 모두 '진술인'이어도 같은 사람이 말을 바꾼 것이 아니다.
GENERIC_SPEAKERS = {
    "보도", "경찰", "가족", "작성자 미상", "진술인", "고소인", "진정인", "고발인", "피해자", "피의자",
    "피고소인", "피고인", "판매자", "구매자", "상대방",
}


def _same_speaker(issue: dict[str, Any], claims: dict[str, dict[str, Any]]) -> bool:
    """모순 난 두 진술이 같은 사람 것인지 — INF-021(진술 간) 과 INF-023(동일인 번복) 을 가른다.

    PairDecision 에는 화자 필드가 없다. 대신 Claim 에 ``speaker`` 가 있으므로
    모순 쌍의 claim_id 두 개를 찾아 화자를 비교한다. 확실할 때만 True — 아니면 INF-021 로 둔다.

    - **기관 문서(접수증 · 통지서)는 번복하는 사람이 아니다.** 화자가 발급 기관(``document_issuer``)이면
      기록끼리 어긋난 것이다. 게다가 기관 이름은 가려져 온다('**경찰서') — 서로 다른 경찰서의
      통지서도 같은 화자로 보인다
    - 가려진 이름('이**')은 다른 사람일 수 있다
    - 역할 · 문서 종류로 적힌 화자('보도', '진술인')는 사람 하나가 아니다
    """
    decision = issue.get("decision") or {}
    a = claims.get(decision.get("claim_a_id")) or {}
    b = claims.get(decision.get("claim_b_id")) or {}
    if "document_issuer" in (a.get("speaker_basis"), b.get("speaker_basis")):
        return False
    who = a.get("speaker")
    if not who or who != b.get("speaker"):
        return False
    return "*" not in who and who not in GENERIC_SPEAKERS and not who.endswith("발급처")


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
