"""수사중지 사건(2021 고소 → 2023 참고인중지 → 2025 목격 제보) 을 끝까지 통과시킨다.

research-engine 의 investigation_suspended 픽스처 출력을 그대로 받는다.
실종 유형(missing)과 달리 송금도 실종 서식도 없고, 결정 이후 새 진술만 들어온 사건이다.
"""

from datetime import date

from action_engine import ST, basis_from_triggers, build_card, to_case_state
from action_engine.codes import INF, TIM
from action_engine.schema import Confidence


def test_결정_통지서에_사유가_적혀_있어도_중지_종류를_가리지_못한다(suspended):
    """통지서에 '수사중지(참고인중지)' 가 있지만 decision_type 항목에는 '수사중지' 만 올라온다.

    research-engine 이 제목 줄의 값을 항목 값으로 고르기 때문이다. 값이 그것뿐이면
    피의자중지·참고인중지를 가를 수 없으므로 확정하지 않고 둘 다 남겨 되묻는다.
    """
    st = to_case_state(suspended).st
    assert st.code == ST.SUSPENDED_SUSPECT
    assert st.confidence is Confidence.PRESUMED
    assert set(st.ambiguous_between) == {ST.SUSPENDED_SUSPECT, ST.SUSPENDED_WITNESS}
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
    assert card.next_action.rule_no == 5
    assert card.next_action.action == "ACT-신규정보제출"
    assert card.next_action.codes == [INF.NEW_STATEMENT]
    assert card.procedure is None  # 절차는 지식베이스의 몫
    # research-engine 이 고른 트리거도 같은 사실을 가리킨다
    assert card.source_trigger["key"] == "investigation_suspended/occurrence/new_fact/unrecorded_fact"


def test_기한은_하나도_계산하지_않는다(suspended):
    """중지 사건에는 불복 기한이 없고, 공소시효는 죄명 없이 계산할 수 없다."""
    deadlines = {d.code: d for d in build_card(suspended).tim}
    assert deadlines[TIM.STATUTE_LIMITATION].due_date is None
    assert "죄명" in deadlines[TIM.STATUTE_LIMITATION].unresolved
    assert all(d.due_date is None for d in deadlines.values())
    assert TIM.ALWAYS_REINVESTIGATION in deadlines  # 상시 가능한 것은 남는다


def test_기산일은_중지_결정일에서_온다(suspended):
    basis = basis_from_triggers(suspended["analysis"]["action_triggers"])
    assert basis.get("decision_time") == date(2023, 2, 9)
