"""우선순위 규칙과 기한 계산 테스트."""

from datetime import date

import pytest

from action_engine import INF, ST, TIM, CaseState, CodeHit, Deadline, compute_deadlines, decide, run
from action_engine.rules import load_deadlines, load_rules


def state(st: str = ST.SUSPENDED_SUSPECT, inf: list[str] | None = None, tim=None) -> CaseState:
    return CaseState(
        case_id="t", case_type="missing_person_suspended", as_of=date(2026, 9, 11),
        st=CodeHit(code=st, label=st, reason="테스트"),
        inf=[CodeHit(code=c, label=c, reason="테스트") for c in (inf or [])],
        tim=tim or [],
    )


# ── 규칙표 자체 ─────────────────────────────────────────────────────────


def test_규칙은_11줄이고_마지막은_기본행동이다():
    rules = load_rules()["rules"]
    assert len(rules) == 11
    assert [r["no"] for r in rules] == list(range(1, 12))
    assert rules[-1]["when"] == {}  # 아무것도 안 맞아도 빈손으로 두지 않는다


def test_모든_규칙에_why가_있다():
    for r in load_rules()["rules"]:
        assert r["why"], f"{r['no']}번 규칙에 근거가 없습니다"


# ── 우선순위 ────────────────────────────────────────────────────────────


def test_단계_미확정이_정보_문제보다_먼저다():
    d = decide(state(st=ST.UNKNOWN, inf=[INF.RECORD_GAP, INF.SOURCE_MISSING]))
    assert d.main.rule_no == 4
    assert d.main.action == "ACT-단계확인"
    assert [h.rule_no for h in d.also] == [9, 10]  # 나머지는 참고사항으로 남는다


def test_신규정보가_모순보다_먼저다():
    d = decide(state(inf=[INF.CONTRADICTION_ACROSS, INF.NEW_FORENSIC]))
    assert d.main.action == "ACT-신규정보제출"
    assert d.also[0].action == "ACT-모순확인"


def test_수사기록_미확인이_근거미비보다_먼저다():
    d = decide(state(inf=[INF.SOURCE_MISSING, INF.RECORD_UNCHECKED]))
    assert d.main.rule_no == 8
    assert d.main.action == "ACT-기록열람"


def test_아무것도_안_맞으면_상시행동이_남는다():
    # 수사가 진행 중이고 정보 문제도 기한도 없는 상태 — 규칙 어느 것도 맞지 않는다
    d = decide(state(st=ST.POLICE_INVESTIGATING, inf=[]))
    assert d.main.action == "ACT-상시"
    assert d.also == []


def test_불복할_수_있는_결정은_기한이_급하지_않아도_안내한다():
    """불송치 이의신청(형사소송법 제245조의7)은 법정 기한이 없다.

    규칙 2는 기한이 급할 때만 발화하므로, 기한이 없는 경로는 영영 급해지지 않아
    한 번도 안내되지 않았다 — 통지를 받고 가장 먼저 열리는 길인데도 그랬다.
    """
    for st in (ST.POLICE_NO_REFERRAL, ST.PROSECUTION_NO_CHARGE, ST.APPEAL_PENDING):
        d = decide(state(st=st, inf=[]))
        assert d.main.action == "ACT-불복기한", st

    # 수사 중에는 불복할 결정이 아직 없다
    assert decide(state(st=ST.POLICE_INVESTIGATING, inf=[])).main.action != "ACT-불복기한"


def test_기한이_급하면_그_규칙이_먼저다():
    """규칙 2(기한 임박)가 규칙 5(결정 받음)보다 앞이라는 것을 고정한다."""
    tim = [Deadline(code=TIM.APPEAL_PROSECUTION, label="항고", severity="critical", days_left=3)]
    d = decide(state(st=ST.PROSECUTION_NO_CHARGE, inf=[], tim=tim))
    assert d.main.rule_no == 2


def test_발화한_규칙번호와_근거코드가_결과에_실린다():
    d = decide(state(inf=[INF.RECORD_GAP]))
    assert d.main.rule_no == 10
    assert d.main.codes == [INF.RECORD_GAP]
    assert d.main.why  # 화면이 그대로 인용한다


# ── 기한 ────────────────────────────────────────────────────────────────


def test_기한값이_비어있으면_Dday를_만들지_않는다():
    """공소시효는 죄명표가 없어 아직 못 채웠다. 그때는 D-day 를 만들지 않는다."""
    t021 = next(t for t in compute_deadlines(state()) if t.code == "TIM-021")
    assert t021.days_left is None
    assert t021.due_date is None
    assert t021.unresolved


def test_기산일을_못_찾으면_이유를_남긴다():
    """기한은 채워졌는데 기산일이 없는 경우 — 항고 기한 30일."""
    t012 = next(t for t in compute_deadlines(state(st=ST.PROSECUTION_NO_CHARGE), {}) if t.code == "TIM-012")
    assert t012.days_left is None
    assert "찾지 못했" in t012.unresolved


def test_불송치_이의신청은_기한이_없다():
    """형사소송법 제245조의7 에 기간 규정이 없다. '못 채운 것'이 아니라 '없는 것'이다."""
    t011 = next(t for t in compute_deadlines(state(st=ST.POLICE_NO_REFERRAL)) if t.code == "TIM-011")
    assert t011.unresolved is None  # 화면에 "확인 필요"를 띄우면 안 된다
    assert t011.severity == "ok"
    assert t011.advisory and "조속한" in t011.advisory
    assert t011.statute == "형사소송법 제245조의7"


def test_채워진_기한은_실제로_계산된다():
    """검찰 항고 30일 — 검찰청법 제10조."""
    t012 = next(
        t for t in compute_deadlines(state(st=ST.PROSECUTION_NO_CHARGE), {"decision_time": date(2026, 9, 1)})
        if t.code == "TIM-012"
    )
    assert t012.period_days == 30
    assert t012.due_date == date(2026, 10, 1)
    assert t012.days_left == 20
    assert t012.severity == "soon"
    assert t012.submit_to and "고등검찰청" in t012.submit_to


def test_검사의_기소중지는_이의제기가_아니라_항고_기한이다():
    """검찰사건사무규칙 제147조 제1항 — 검사의 기소중지 · 참고인중지는 항고 대상이다."""
    def codes(issuer):
        st = CaseState(case_id="t", case_type="missing_person_suspended", as_of=date(2026, 9, 11),
                       st=CodeHit(code=ST.SUSPENDED_SUSPECT, label="", reason="테스트", issuer=issuer))
        return {t.code for t in compute_deadlines(st, {"decision_time": date(2026, 9, 1)})}

    assert "TIM-012" in codes("prosecution") and "TIM-014" not in codes("prosecution")
    assert "TIM-014" in codes("police") and "TIM-012" not in codes("police")
    assert "TIM-014" in codes(None)  # 기관을 모르는 수사중지는 수사권 조정 뒤의 경찰 결정으로 본다


def test_재정신청은_10일이다():
    """형사소송법 제260조 제3항."""
    t013 = next(
        t for t in compute_deadlines(state(st=ST.APPEAL_PENDING), {"decision_time": date(2026, 9, 8)})
        if t.code == "TIM-013"
    )
    assert t013.period_days == 10
    assert t013.due_date == date(2026, 9, 18)
    assert t013.days_left == 7
    assert t013.severity == "critical"  # 7일 이하


def test_죄명이_필요한_공소시효는_계산하지_않는다():
    tims = compute_deadlines(state(), {"incident_end": date(2015, 10, 10)})
    t021 = next(t for t in tims if t.code == "TIM-021")
    assert t021.days_left is None
    assert "죄명" in t021.unresolved


def test_상시_항목은_기한없음으로_둔다():
    tims = compute_deadlines(state())
    always = [t for t in tims if t.code in ("TIM-041", "TIM-042")]
    assert len(always) == 2
    assert all(t.severity == "ok" and t.unresolved is None for t in always)


def test_단계에_맞는_기한만_나온다():
    codes = {t.code for t in compute_deadlines(state(st=ST.POLICE_NO_REFERRAL))}
    assert "TIM-011" in codes  # 불송치 → 이의신청
    assert "TIM-012" not in codes  # 불기소 기한은 해당 없음


def test_기한에는_반드시_출처가_붙는다():
    """출처 없는 기한은 넣지 않는다. 값을 추측으로 채우지 못하게 막는 장치."""
    kb = load_deadlines()
    assert kb["status"] == "draft_unverified"  # 법률 전문가 검수 전
    for row in kb["deadlines"]:
        if row.get("period_days") is not None:
            assert row.get("statute"), f"{row['code']} 에 근거 법령이 없습니다"
            assert row.get("source"), f"{row['code']} 에 출처 URL 이 없습니다"


def test_기한없음과_못채움을_구별한다():
    """'법정 기한 없음'과 '아직 못 채움'은 다른 상태다.

    사용자에게 "기한 제한이 없습니다"는 그 자체로 필요한 정보이고,
    "아직 확인 못 했습니다"는 화면에 아무것도 띄우면 안 되는 상태다.
    """
    rows = {r["code"]: r for r in load_deadlines()["deadlines"]}
    assert rows["TIM-011"]["no_statutory_limit"] is True  # 불송치 이의신청 — 조문에 기간 규정 없음
    assert rows["TIM-021"].get("no_statutory_limit") is None  # 공소시효 — 있는데 못 채운 것
    assert rows["TIM-021"]["period_days"] is None


def test_수사중지_이의제기는_30일이다():
    """장기·미제 사건의 출발점. 경찰수사규칙 제101조."""
    t014 = next(
        t for t in compute_deadlines(state(st=ST.SUSPENDED_SUSPECT), {"decision_time": date(2026, 9, 1)})
        if t.code == "TIM-014"
    )
    assert t014.period_days == 30
    assert t014.due_date == date(2026, 10, 1)
    assert t014.severity == "soon"
    assert "상급경찰관서" in t014.submit_to  # 결정한 경찰서가 아니다
    assert "제101조" in t014.statute


def test_수사중지_기한임박이_규칙2번을_발화시킨다():
    """TIM-014 를 만들기 전에는 이 상태에서 기한 규칙이 아예 안 걸렸다."""
    s = state(st=ST.SUSPENDED_SUSPECT)
    s.tim = compute_deadlines(s, {"decision_time": date(2026, 8, 18)})  # 30일 중 6일 남음
    d = decide(s)
    assert d.main.rule_no == 2
    assert d.main.action == "ACT-불복기한"
    assert "TIM-014" in d.main.codes


def test_이미_지난_기한은_다음_행동이_되지_않는다():
    """닫힌 경로를 '지금 하세요'로 안내하면 안 된다.

    장기·미제 사건은 결정이 몇 년 전인 경우가 대부분이라 기한이 지나 있다.
    그때 "이의제기 하세요"를 1순위로 띄우면 잘못된 안내가 된다.
    만료 사실은 tim 목록에 남으므로 화면이 따로 알릴 수 있다.
    """
    s = state(st=ST.SUSPENDED_SUSPECT, inf=[INF.NEW_STATEMENT])
    s.tim = compute_deadlines(s, {"decision_time": date(2022, 3, 15)})  # 4년 전
    t014 = next(t for t in s.tim if t.code == "TIM-014")
    assert t014.severity == "expired"  # 만료 사실은 남는다

    d = decide(s)
    assert d.main.rule_no == 6  # 기한이 아니라 신규 정보가 1순위
    assert d.main.action == "ACT-신규정보제출"
    assert not any("TIM-014" in h.codes for h in [d.main, *d.also])


def test_정정_내역을_기록으로_남긴다():
    """수집 자료를 고친 곳은 근거와 함께 남긴다. 나중에 왜 바꿨는지 추적할 수 있어야 한다."""
    corrections = load_deadlines()["corrections"]
    assert len(corrections) >= 2
    for c in corrections:
        assert c["fixed"] and c["why_it_matters"] and c["verified_at"]


def test_기한이_채워지면_계산된다(monkeypatch):
    """지식베이스가 채워졌을 때 동작을 미리 고정해 둔다."""
    from action_engine import rules as R

    R.load_deadlines.cache_clear()
    monkeypatch.setattr(R, "load_deadlines", lambda: {
        "deadlines": [{"code": "TIM-011", "applies_to_st": ["ST-301"], "basis": "decision_time",
                       "basis_label": "통지 수령일", "period_days": 30, "statute": "○○법 §1"}]
    })
    tims = R.compute_deadlines(state(st=ST.POLICE_NO_REFERRAL), {"decision_time": date(2026, 9, 1)})
    t = tims[0]
    assert t.due_date == date(2026, 10, 1)
    assert t.days_left == 20
    assert t.severity == "soon"


@pytest.mark.parametrize("days,expected", [(-1, "expired"), (0, "critical"), (7, "critical"),
                                           (8, "soon"), (30, "soon"), (31, "ok")])
def test_등급_경계(days, expected):
    from action_engine.rules import _severity

    assert _severity(days) == expected


# ── 전체 ────────────────────────────────────────────────────────────────


def test_실제_출력으로_끝까지_돈다(missing):
    d = run(missing)
    assert d.state.st.code == ST.SUSPENDED_SUSPECT
    assert d.main is not None and d.main.why
    assert d.state.tim
    # 수사중지 이의제기 30일은 계산되지만 2022년 결정이라 이미 지났다
    t014 = next(t for t in d.state.tim if t.code == "TIM-014")
    assert t014.severity == "expired"
    tim = {t.code: t for t in d.state.tim}
    # 통지서의 죄명이 '약취유인'뿐이라 법정형을 고를 수 없다 — 대상 · 목적을 짐작하지 않는다
    assert tim["TIM-021"].days_left is None and "약취유인" in tim["TIM-021"].unresolved
    # 통신 기록 보존은 2015-10 마지막 연락부터 세어 이미 지났다
    assert tim["TIM-031"].severity == "expired"


# ── 통신자료 보존(TIM-031)의 기산일 ─────────────────────────────────────


def test_보존_기한은_메신저_대화일부터_센다(fraud):
    """통신비밀보호법 시행령 제41조 — 통신사실확인자료는 통신이 있었던 날부터 보존한다."""
    t031 = {t.code: t for t in run(fraud).state.tim}["TIM-031"]
    assert t031.basis_date == date(2026, 6, 1)
    assert t031.due_date == date(2026, 8, 30)
    assert "메신저 대화" in t031.advisory


def test_보존_기한은_다음으로_사라질_기록을_기준으로_한다():
    """이미 사라진 기록을 기준으로 삼으면 남은 기록까지 없다고 안내하게 된다."""
    from action_engine.rules import retention_basis

    dates = [(date(2026, 1, 5), "옛 대화"), (date(2026, 7, 1), "최근 대화"), (date(2026, 8, 20), "마지막 연락")]
    when, note = retention_basis(dates, 90, as_of=date(2026, 9, 11))
    assert when == date(2026, 7, 1)  # 1월 기록은 이미 지났고, 7월 기록이 가장 먼저 사라진다
    assert "2026-11-18" in note  # 마지막 연락(8/20) 기록이 남는 날
    assert "이미 보존 기간이 지났습니다" in note

    when, _ = retention_basis(dates[:1], 90, as_of=date(2026, 9, 11))
    assert when == date(2026, 1, 5)  # 전부 지났으면 가장 늦은 날 — 만료로 보인다


def test_화면에_적은_메모만으로는_보존_기한을_세지_않는다():
    from action_engine.rules import communication_dates

    result = {"documents": [{"doc_id": "n", "doc_type": "user_note", "file_name": "직접 입력"}],
              "extraction": {"claims": [{"doc_id": "n", "evidence_level": "user", "slot": "last_contact_time",
                                         "slot_time": {"start": "2026-06-02T00:00:00"}}]}}
    assert communication_dates(result) == []


def test_사기_사건도_끝까지_돈다(fraud):
    d = run(fraud)
    assert d.main is not None
    # 기록에 반영 안 된 자료가 없으므로 INF-01 은 켜지지 않고, 송금액 모순이 먼저 잡힌다
    assert d.main.rule_no == 7
    assert d.main.action == "ACT-모순확인"
    assert d.main.codes == [INF.CONTRADICTION_ACROSS]


def test_사건이_다르면_다른_행동이_나온다(missing, fraud):
    """우선순위 표가 실제로 갈라지는지. 둘 다 같은 규칙이 나오면 표가 무의미하다."""
    a, b = run(missing), run(fraud)
    assert a.main.rule_no != b.main.rule_no
    assert a.main.action == "ACT-신규정보제출"  # 2019 목격 진술이 2022 통지서에 반영 안 됨
    assert b.main.action == "ACT-모순확인"  # 송금액이 자료마다 다름
