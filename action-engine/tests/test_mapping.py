"""research-engine 출력 → ST·INF 변환 (A안) 테스트."""

from action_engine import INF, ST, Confidence, resolve_inf, resolve_st, to_case_state

# ── ST ──────────────────────────────────────────────────────────────────


def test_수사중지_결정을_ST200대로_옮긴다(missing):
    st = resolve_st(missing)
    # decision_type 값이 '수사중지' 뿐이라 피의자·참고인 구분이 안 된다 → 추정으로 두고 둘 다 남긴다
    assert st.code == ST.SUSPENDED_SUSPECT
    assert st.confidence is Confidence.PRESUMED
    assert set(st.ambiguous_between) == {ST.SUSPENDED_SUSPECT, ST.SUSPENDED_WITNESS}
    assert "수사중지" in st.reason
    assert "suspension_notice_2022" in st.source_doc_ids


def test_결정내용이_없으면_단계로_추정한다(fraud):
    st = resolve_st(fraud)
    # 접수 단계까지만 있고 결정 내용이 없다 → 확정하지 않는다
    assert st.confidence is Confidence.PRESUMED
    assert st.code == ST.POLICE_INVESTIGATING


def test_결정내용_문자열로_단계가_갈린다():
    def case(value: str, state: str = "confirmed") -> str:
        return resolve_st({
            "analysis": {"slot_statuses": [
                {"slot": "decision_type", "value": value, "state": state, "stage": "outcome",
                 "required": True, "sources": []}
            ]},
            "timeline": {"current_stage": "outcome"},
        }).code

    assert case("불송치") == ST.POLICE_NO_REFERRAL
    assert case("불기소") == ST.PROSECUTION_NO_CHARGE
    assert case("혐의없음") == ST.PROSECUTION_NO_CHARGE
    assert case("이의신청 접수") == ST.APPEAL_PENDING
    assert case("재정신청") == ST.ADJUDICATION_REQUEST
    assert case("참고인중지") == ST.SUSPENDED_WITNESS
    assert case("피의자중지") == ST.SUSPENDED_SUSPECT


def test_결정내용이_흔들리면_확정으로_올리지_않는다():
    st = resolve_st({
        "analysis": {"slot_statuses": [
            {"slot": "decision_type", "value": "불송치", "state": "conflicting", "stage": "outcome",
             "required": True, "sources": []}
        ]},
        "timeline": {"current_stage": "outcome"},
    })
    assert st.code == ST.POLICE_NO_REFERRAL
    assert st.confidence is Confidence.PRESUMED


def test_판정_못하면_추측하지_않는다():
    st = resolve_st({"analysis": {"slot_statuses": []}, "timeline": {"current_stage": "outcome"}})
    assert st.code == ST.UNKNOWN
    assert st.confidence is Confidence.UNDETERMINED
    assert "통지서" in st.reason


# ── INF ─────────────────────────────────────────────────────────────────


def test_기록에_반영안된_자료만_신규정보로_본다(missing):
    """자료함에 문서가 있다는 것만으로는 INF-01 이 켜지지 않는다.

    2019년 목격자 진술이 2022년 수사중지 결정 통지서에 반영되지 않았다는
    unrecorded_fact 판정이 있을 때만, 그 근거 문서의 종류로 INF-01* 를 정한다.
    """
    hits = {h.code: h for h in resolve_inf(missing)}
    assert INF.NEW_STATEMENT in hits  # 2019 목격자 진술서 · 2023 진정서
    assert hits[INF.NEW_STATEMENT].source_trigger_keys  # unrecorded_fact 트리거가 근거
    assert "unrecorded_fact" in hits[INF.NEW_STATEMENT].source_trigger_keys[0]
    # 접수증·보도는 기록에 이미 반영된 자료다 → 신규 정보가 아니다
    assert INF.NEW_PHYSICAL not in hits
    assert INF.NEW_MEDIA not in hits


def test_반영안된_자료가_없으면_신규정보는_켜지지_않는다(fraud):
    """사기 사건에는 unrecorded_fact 가 없다. 자료가 6개 있어도 INF-01 은 안 켜진다."""
    codes = {h.code for h in resolve_inf(fraud)}
    assert not (codes & {INF.NEW_STATEMENT, INF.NEW_PHYSICAL, INF.NEW_FORENSIC, INF.NEW_MEDIA})


def test_기록공백과_수사기록_미확인을_잡는다(missing):
    hits = {h.code: h for h in resolve_inf(missing)}
    assert INF.RECORD_GAP in hits  # time_gap / stage_skipped
    assert INF.RECORD_UNCHECKED in hits  # stage_stalled / possibly_outdated / unrecorded_fact
    assert hits[INF.RECORD_UNCHECKED].source_trigger_keys  # 근거 트리거가 붙어 있다


def test_송금액_모순은_진술간_모순으로_옮긴다(fraud):
    hits = {h.code: h for h in resolve_inf(fraud)}
    assert INF.CONTRADICTION_ACROSS in hits
    assert any("transfer_amount" in k for k in hits[INF.CONTRADICTION_ACROSS].source_trigger_keys)


def _conflict(speaker_a: str, speaker_b: str) -> dict:
    return {
        "documents": [],
        "extraction": {"claims": [
            {"claim_id": "c1", "speaker": speaker_a},
            {"claim_id": "c2", "speaker": speaker_b},
        ]},
        "analysis": {"issues": [{
            "condition": "conflicting", "message": "값이 엇갈립니다", "sources": [],
            "trigger": {"key": "x/conflicting"},
            "decision": {"claim_a_id": "c1", "claim_b_id": "c2"},
        }]},
    }


def test_같은_화자가_말을_바꾸면_동일인_번복이다():
    """PairDecision 에 화자 필드가 없어 Claim.speaker 로 가른다."""
    codes = {h.code for h in resolve_inf(_conflict("김민수", "김민수"))}
    assert INF.CONTRADICTION_SELF in codes
    assert INF.CONTRADICTION_ACROSS not in codes


def test_다른_화자면_진술_간_모순이다():
    codes = {h.code for h in resolve_inf(_conflict("김민수", "최영호"))}
    assert INF.CONTRADICTION_ACROSS in codes
    assert INF.CONTRADICTION_SELF not in codes


def test_화자를_모르면_동일인으로_올리지_않는다():
    codes = {h.code for h in resolve_inf(_conflict("", ""))}
    assert INF.CONTRADICTION_ACROSS in codes
    assert INF.CONTRADICTION_SELF not in codes


def test_감정자료가_없으면_전문분석_미실시(missing, fraud):
    for result in (missing, fraud):
        assert INF.ANALYSIS_NOT_DONE in {h.code for h in resolve_inf(result)}


def test_대응코드가_없는_조건은_옮기지_않는다():
    """identity_unconfirmed 는 우리 INF 에 대응 코드가 없다. 억지로 매칭하지 않는다."""
    hits = resolve_inf({
        "documents": [],
        "analysis": {"issues": [
            {"condition": "identity_unconfirmed", "message": "동일인 여부 미확인",
             "sources": [], "trigger": {"key": "x/identity_unconfirmed"}}
        ]},
    })
    assert not [h for h in hits if h.source_trigger_keys]


def test_모든_INF에_근거가_붙는다(missing, fraud):
    for result in (missing, fraud):
        for hit in resolve_inf(result):
            assert hit.reason, f"{hit.code} 에 근거 문장이 없습니다"


# ── 전체 ────────────────────────────────────────────────────────────────


def test_사건상태로_옮긴다(missing):
    state = to_case_state(missing)
    assert state.case_type == "missing_person_suspended"
    assert state.as_of.year == 2026
    assert state.st.code == ST.SUSPENDED_SUSPECT
    assert len(state.inf) >= 5
