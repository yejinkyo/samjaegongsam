"""research-engine 출력 → ST·INF 변환 (A안) 테스트."""

import pytest

from action_engine import INF, ST, Confidence, resolve_inf, resolve_st, to_case_state

# ── ST ──────────────────────────────────────────────────────────────────


def test_수사중지_결정을_ST200대로_옮긴다(missing):
    st = resolve_st(missing)
    # 통지서 결정내용란의 '수사중지(피의자중지)' 가 항목 값으로 올라온다 → 사유까지 확정된다
    assert st.code == ST.SUSPENDED_SUSPECT
    assert st.confidence is Confidence.CONFIRMED
    assert not st.ambiguous_between
    assert "수사중지(피의자중지)" in st.reason
    assert "suspension_notice_2022" in st.source_doc_ids


def test_사유가_없으면_중지_종류를_가르지_않는다():
    """통지서에 '수사중지' 만 적혀 있는 경우 — 추정으로 두고 둘 다 남겨 되묻는다."""
    st = resolve_st({
        "analysis": {"slot_statuses": [
            {"slot": "decision_type", "value": "수사중지", "state": "confirmed", "stage": "outcome",
             "required": True, "sources": []}
        ]},
        "timeline": {"current_stage": "outcome"},
    })
    assert st.code == ST.SUSPENDED_SUSPECT
    assert st.confidence is Confidence.PRESUMED
    assert set(st.ambiguous_between) == {ST.SUSPENDED_SUSPECT, ST.SUSPENDED_WITNESS}


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
    assert case("혐의없음") == ST.UNKNOWN  # 경찰도 검찰도 쓰는 말 — 낸 기관을 모르면 고르지 않는다
    assert case("이의신청 접수") == ST.APPEAL_PENDING
    assert case("재정신청") == ST.ADJUDICATION_REQUEST
    assert case("참고인중지") == ST.SUSPENDED_WITNESS
    assert case("피의자중지") == ST.SUSPENDED_SUSPECT


def _decided(value: str, speaker: str | None = None, when: str | None = None):
    slots = [{"slot": "decision_type", "value": value, "state": "confirmed", "stage": "outcome", "required": True,
              "claim_ids": ["n:c1"], "sources": [{"source_doc_id": "n"}]}]
    if when:
        slots.append({"slot": "decision_time", "value": when, "state": "confirmed", "stage": "outcome",
                      "required": True, "sources": []})
    claims = [{"claim_id": "n:c1", "speaker": speaker}] if speaker else []
    return resolve_st({"analysis": {"slot_statuses": slots}, "extraction": {"claims": claims},
                       "timeline": {"current_stage": "outcome"}})


def test_혐의없음은_통지서를_낸_기관으로_가른다():
    """'혐의없음'은 경찰 불송치와 검찰 불기소에 함께 쓰는 사유다. 낸 기관이 다르면 불복 절차도 다르다."""
    police = _decided("혐의없음", speaker="**경찰서")
    assert police.code == ST.POLICE_NO_REFERRAL and police.issuer == "police"
    prosecution = _decided("혐의없음", speaker="**지방검찰청")
    assert prosecution.code == ST.PROSECUTION_NO_CHARGE and prosecution.issuer == "prosecution"


def test_수사권_조정_전_결정은_검찰의_결정이다():
    """2021-01-01 전에는 경찰에 불송치 결정권이 없었다."""
    old = _decided("혐의없음", when="2019-05-02")
    assert old.code == ST.PROSECUTION_NO_CHARGE and old.issuer == "prosecution"


def test_낸_기관을_모르면_단계를_고르지_않는다():
    unknown = _decided("혐의없음", speaker="notice.png 발급처", when="2024-03-01")
    assert unknown.code == ST.UNKNOWN
    assert unknown.confidence is Confidence.UNDETERMINED
    assert set(unknown.ambiguous_between) == {ST.POLICE_NO_REFERRAL, ST.PROSECUTION_NO_CHARGE}


def test_결정_문구가_기관을_밝히면_그걸_따른다():
    assert _decided("불송치(혐의없음)", speaker="**지방검찰청").code == ST.POLICE_NO_REFERRAL
    stop = _decided("기소중지")
    assert stop.code == ST.SUSPENDED_SUSPECT and stop.issuer == "prosecution"
    assert "항고" in stop.reason


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


def test_신규정보의_이유는_가장_최근_자료로_쓴다():
    """반영 안 된 진술이 여럿이면 가장 늦게 일어난 일이 이유가 된다 — 새 정보에 가장 가깝다."""
    def issue(doc_id, event_id):
        return {"condition": "unrecorded_fact", "sources": [{"source_doc_id": doc_id}],
                "related_event_ids": [event_id], "trigger": {"key": f"k/{doc_id}"}}
    result = {
        "documents": [{"doc_id": "old", "doc_type": "statement", "file_name": "진술서_2017.jpg"},
                      {"doc_id": "new", "doc_type": "statement", "file_name": "진술서_2025.jpg"}],
        "timeline": {"events": [{"timeline_event_id": "tl1", "time": {"start": "2017-11-02T21:00:00"}},
                                {"timeline_event_id": "tl2", "time": {"start": "2025-08-14T12:00:00"}}]},
        "analysis": {"issues": [issue("old", "tl1"), issue("new", "tl2")]},
    }
    hits = {h.code: h for h in resolve_inf(result)}
    assert hits[INF.NEW_STATEMENT].reason.startswith("진술서_2025.jpg")


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


def _conflict(speaker_a: str, speaker_b: str, basis: str = "document_author") -> dict:
    return {
        "documents": [],
        "extraction": {"claims": [
            {"claim_id": "c1", "speaker": speaker_a, "speaker_basis": basis},
            {"claim_id": "c2", "speaker": speaker_b, "speaker_basis": basis},
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


def test_기관_문서끼리_어긋난_것은_동일인_번복이_아니다():
    """접수증과 통지서가 다르면 기록끼리 어긋난 것이다. 게다가 기관 이름은 '**경찰서'로 가려져 와서
    서로 다른 경찰서의 문서도 같은 화자로 보인다."""
    codes = {h.code for h in resolve_inf(_conflict("**경찰서", "**경찰서", basis="document_issuer"))}
    assert INF.CONTRADICTION_ACROSS in codes
    assert INF.CONTRADICTION_SELF not in codes


@pytest.mark.parametrize("who", ["보도", "진술인", "작성자 미상", "이**"])
def test_사람_하나를_가리키지_않는_화자는_동일인으로_보지_않는다(who):
    """두 기사가 모두 '보도', 이름을 못 찾은 두 진술서가 모두 '진술인'이어도 같은 사람이 아니다."""
    codes = {h.code for h in resolve_inf(_conflict(who, who))}
    assert INF.CONTRADICTION_SELF not in codes


def test_감정이_핵심인_사건에_감정자료가_없으면_전문분석_미실시(missing):
    """실종 사건은 유전자 · 유류품 감정이 수사의 핵심이다."""
    assert INF.ANALYSIS_NOT_DONE in {h.code for h in resolve_inf(missing)}


def test_감정이_필요_없는_사건에는_전문분석_미실시를_켜지_않는다(fraud):
    """모든 사건에 켜면 대부분의 사기 사건이 늘 9번(근거보완)으로 떨어져 10 · 11 · 12번에 닿지 않는다."""
    assert INF.ANALYSIS_NOT_DONE not in {h.code for h in resolve_inf(fraud)}


def test_감정서를_올리면_전문분석_미실시가_꺼진다(missing):
    import copy

    result = copy.deepcopy(missing)
    result["documents"].append({"doc_id": "f1", "doc_type": "forensic", "file_name": "감정서.jpg"})
    assert INF.ANALYSIS_NOT_DONE not in {h.code for h in resolve_inf(result)}


def test_결정_전_사건의_결정_없음은_근거_미비가_아니다():
    """수사 중인 사건에 '결정 내용'이 없는 것은 결정이 아직 없어서다. 결과 단계에 온 사건만 빠진 것으로 본다."""
    def result(stage):
        return {"documents": [], "extraction": {"claims": []}, "timeline": {"current_stage": stage},
                "analysis": {"issues": [{"condition": "missing", "stage": "outcome", "slot": "decision_type",
                                         "message": "결정 내용: 올린 자료에서 찾지 못했습니다", "sources": []}]}}

    assert INF.SOURCE_MISSING not in {h.code for h in resolve_inf(result("investigation"))}
    assert INF.SOURCE_MISSING in {h.code for h in resolve_inf(result("outcome"))}


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


def test_불송치_혐의없음은_경찰_불송치다():
    """'혐의없음'은 불송치의 이유이지 검찰의 불기소 처분이 아니다.

    통지서에 '불송치(혐의없음)' 으로 적혀 온다. 검찰 불기소로 보면 경찰에 낼 이의신청
    대신 검찰 항고를 안내하게 되고, 실제로 열려 있는 불복 경로를 놓친다.
    """
    from action_engine.mapping import st_from_decision

    assert st_from_decision("불송치(혐의없음)").code == ST.POLICE_NO_REFERRAL
    assert st_from_decision("불송치").code == ST.POLICE_NO_REFERRAL
    # 불송치가 아닌 '혐의없음'은 그대로 검찰 불기소다
    assert st_from_decision("혐의없음").code == ST.PROSECUTION_NO_CHARGE
    assert st_from_decision("불기소(혐의없음)").code == ST.PROSECUTION_NO_CHARGE


def test_2021년_이전_결정_문구를_알아듣는다():
    """'기소중지'·'기소유예'에도 '기소'가 들어 있지만 재판 중이 아니다. 장기·미제 사건 서류에 흔한 말이다."""
    from action_engine.mapping import st_from_decision

    assert st_from_decision("기소중지").code == ST.SUSPENDED_SUSPECT
    assert st_from_decision("기소중지").confidence is Confidence.CONFIRMED  # 피의자를 찾지 못해 멈춘 것 — 사유가 분명하다
    assert st_from_decision("참고인중지").code == ST.SUSPENDED_WITNESS
    assert st_from_decision("기소유예").code == ST.PROSECUTION_NO_CHARGE
    assert st_from_decision("불기소(기소유예)").code == ST.PROSECUTION_NO_CHARGE
    assert st_from_decision("무혐의").code == ST.PROSECUTION_NO_CHARGE
    assert st_from_decision("각하").code == ST.PROSECUTION_NO_CHARGE
    assert st_from_decision("불송치(각하)").code == ST.POLICE_NO_REFERRAL
    # 송치는 검찰로 넘어간 것 — 불기소 의견이 붙어도 검사는 아직 결정하지 않았다
    assert st_from_decision("송치").code == ST.PROSECUTION_INVESTIGATING
    assert st_from_decision("불기소의견송치").code == ST.PROSECUTION_INVESTIGATING
    assert st_from_decision("기소의견 송치").code == ST.PROSECUTION_INVESTIGATING
    # 내사종결은 입건되지 않고 끝난 것 — 단계는 추정으로만 둔다
    closed = st_from_decision("내사종결")
    assert closed.code == ST.PRE_INVESTIGATION and closed.confidence is Confidence.PRESUMED
    # 원래 뜻은 그대로다
    assert st_from_decision("공소제기").code == ST.TRIAL_ONGOING
    assert st_from_decision("구약식 기소").code == ST.TRIAL_ONGOING
