"""수사중지 사건(2021 고소 → 2023 참고인중지 → 2025 목격 제보) 을 끝까지 통과시킨다.

research-engine 의 investigation_suspended 픽스처 출력을 그대로 받는다.
실종 유형(missing)과 달리 송금도 실종 서식도 없고, 결정 이후 새 진술만 들어온 사건이다.
"""

from datetime import date

from action_engine import ST, basis_from_triggers, build_card, to_case_state
from action_engine.codes import INF, TIM
from action_engine.schema import Confidence


def test_통지서의_중지_사유로_참고인중지를_가른다(suspended):
    """통지서 결정내용란의 '수사중지(참고인중지)' 가 그대로 항목 값으로 올라온다.

    사유가 없으면 피의자중지·참고인중지를 가를 수 없어 되물어야 한다
    (``test_사유가_없으면_중지_종류를_가르지_않는다``).
    """
    st = to_case_state(suspended).st
    assert st.code == ST.SUSPENDED_WITNESS
    assert st.confidence is Confidence.CONFIRMED
    assert not st.ambiguous_between
    assert set(st.source_doc_ids) == {"suspension_notice_2023"}


def test_중지_이후의_새_진술을_신규_인적_진술로_받는다(suspended):
    state = to_case_state(suspended)
    codes = {h.code for h in state.inf}
    assert INF.NEW_STATEMENT in codes  # 2025 목격 진술서 (기록에서 확인되지 않는 사실)
    assert INF.RECORD_GAP in codes  # 수사 단계 자료 없음 · 기록 공백
    assert INF.RECORD_UNCHECKED in codes  # 수사 기록에 반영됐는지 미확인
    assert INF.CONTRADICTION_ACROSS not in codes  # 모순은 없는 사건이다
    new_statement = next(h for h in state.inf if h.code == INF.NEW_STATEMENT)
    assert new_statement.source_doc_ids == ["witness_statement_2025"]


def test_다음_행동은_신규_정보_제출이다(suspended):
    card = build_card(suspended)
    assert card.next_action.rule_no == 6
    assert card.next_action.action == "ACT-신규정보제출"
    assert card.next_action.codes == [INF.NEW_STATEMENT]
    assert card.procedure is None  # 절차는 지식베이스의 몫
    # research-engine 이 고른 트리거도 같은 사실을 가리킨다
    assert card.source_trigger["key"] == "investigation_suspended/occurrence/new_fact/unrecorded_fact"


def test_이의제기_기한은_이미_지났고_공소시효는_통지서의_죄명으로_계산한다(suspended):
    """중지 사건에도 불복 기한이 있다 — 통지 수령일부터 30일(경찰수사규칙 제101조).

    2023년 결정이라 이미 지났다. 만료 사실은 남기되 '다음 행동'으로는 올리지 않는다.
    공소시효는 통지서의 죄명(사기 · 10년)과 고소장에 적힌 피해일(2021-05-18)로 계산한다.
    피해일이 기록으로 확인된 날이 아니라는 사실은 숨기지 않는다.
    """
    deadlines = {d.code: d for d in build_card(suspended).tim}
    t014 = deadlines[TIM.APPEAL_SUSPENSION]
    assert t014.period_days == 30
    assert t014.severity == "expired"
    assert "상급경찰관서" in t014.submit_to

    limitation = deadlines[TIM.STATUTE_LIMITATION]
    assert limitation.unresolved is None
    assert limitation.statute == "형법 제347조 제1항"
    assert limitation.due_date == date(2031, 5, 17)  # 초일 산입 — 10년 뒤 같은 날의 전날
    assert "진술에 적힌 가장 이른 날(2021-05-18)" in limitation.advisory
    assert TIM.ALWAYS_REINVESTIGATION in deadlines  # 상시 가능한 것은 남는다


def test_기산일은_중지_결정일에서_온다(suspended):
    basis = basis_from_triggers(suspended["analysis"]["action_triggers"])
    assert basis.get("decision_time") == date(2023, 2, 9)
