"""재수사가 한 번 열렸다가 다시 중지된 장기 미제 실종 사건 통합 테스트. 등장인물·사건은 가상이다.

long_unsolved_missing 과 다른 점은 **같은 항목의 값이 시간에 따라 여러 번 바뀐다**는 것이다
(사건번호 2개 · 담당 수사관 2명 · 수사중지 결정 2번). 지금 엔진이 그걸 어떻게 다루는지를
여기 고정해 둔다. 픽스처 README 의 '놓쳤거나 잘못 잡았다' 항목이 아래 테스트와 1:1로 대응한다.
"""

import pytest

from research_engine.pipeline import ResearchPipeline, load_case
from research_engine.schema import ClaimSlot, ClarificationKind, GapCondition, IssueCategory, SlotState, Stage

from .conftest import FIXTURES


@pytest.fixture(scope="module")
def result():
    return ResearchPipeline().run(load_case(FIXTURES / "long_unsolved_reopened" / "case.json"))


def test_late_tip_is_flagged_as_unrecorded_fact(result):
    # 직접 적은 메모도 타임라인에 오르게 되면서(note_no_contact) 이 조건이 둘이 되었다.
    # 여기서 보는 것은 제보 진술 쪽 하나다.
    [issue] = [i for i in result.analysis.issues
               if i.condition is GapCondition.UNRECORDED_FACT
               and {s.source_doc_id for s in i.sources} == {"tip_statement_2021"}]
    assert issue.category is IssueCategory.UNVERIFIED
    assert issue.trigger.key == "missing_person_suspended/occurrence/new_fact/unrecorded_fact"
    assert {s.source_doc_id for s in issue.sources} == {"tip_statement_2021"}
    assert "2022-09-14" in issue.message and "앞선" in issue.message  # 2차 중지 결정보다 앞선 내용
    assert issue.trigger.since.year == 2006  # '2007년 1월경' 이 2006-12-17~2007-02-15 범위로 풀린다


def test_investigator_change_marks_the_2019_record_outdated(result):
    issue = next(i for i in result.analysis.issues if i.condition is GapCondition.POSSIBLY_OUTDATED)
    assert issue.slot is ClaimSlot.INVESTIGATOR
    assert "문상철" in issue.message and "2O24년 봄 담당 형사가 또 바뀌었다고 함" in issue.message
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.INVESTIGATOR].state is SlotState.OUTDATED


def test_elapsed_time_since_the_second_suspension(result):
    stalled = next(i for i in result.analysis.issues if i.condition is GapCondition.STAGE_STALLED)
    assert stalled.trigger.stage is Stage.OUTCOME and stalled.trigger.elapsed_days == 1463
    assert stalled.trigger.since.date().isoformat() == "2022-09-14"


def test_last_seen_time_difference_stays_suspected(result):
    """접수증 23:20 vs 보도 '11/5 0:30경'. '경' 이 범위로 풀려 확정 불일치까지는 가지 않는다."""
    issue = next(i for i in result.analysis.issues if i.slot is ClaimSlot.LAST_SEEN_TIME)
    assert issue.condition is GapCondition.SUSPECTED_CONFLICT
    assert {s.source_doc_id for s in issue.sources} == {"missing_report_2006", "news_2016"}
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.LAST_SEEN_TIME].value == "2006-11-04 23:20"  # 기록 자료 쪽을 대표로 세운다


def test_unreadable_lines_and_unknown_form_are_asked_back(result):
    pending = {q.request_id: q for q in result.clarifications if q.status == "pending"}
    assert set(pending) == {"missing_report_2006:u8:q", "family_memo:u4:q", "dna_receipt_2025:q-doctype"}
    assert pending["dna_receipt_2025:q-doctype"].kind is ClarificationKind.DOCUMENT_TYPE
    assert pending["family_memo:u4:q"].kind is ClarificationKind.UNREADABLE_TEXT


def test_the_latest_decision_is_the_current_state(result):
    """결정이 두 번(2008 피의자중지 → 2022 참고인중지)이면 가장 최근 통지서가 지금 상태다.

    옛 결정이 대표값이 되면 기능 2 가 ST-201(피의자중지)을 기준으로 다음 행동을 고른다.
    """
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.DECISION_TYPE].state is SlotState.CONFIRMED
    assert slots[ClaimSlot.DECISION_TYPE].value == "수사중지(참고인중지)"  # 2022 통지서
    assert slots[ClaimSlot.DECISION_TIME].state is SlotState.CONFIRMED
    assert slots[ClaimSlot.DECISION_TIME].value == "2022-09-14"


def test_values_that_changed_over_time_are_not_conflicts(result):
    """재입건 뒤 새 사건번호 · 담당 수사관 교체 · 두 번의 결정은 어긋난 게 아니라 차례다.

    서로 다른 때 나온 통지서끼리는 비교하지 않고, 가장 최근 통지서의 값을 지금 값으로 쓴다.
    진정서가 지금 사건번호를 적은 것도 재입건 전 옛 번호와 어긋난 것으로 보지 않는다.
    """
    assert not [i for i in result.analysis.issues if i.condition is GapCondition.CONFLICTING]
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.CASE_NUMBER].state is SlotState.CONFIRMED
    assert slots[ClaimSlot.CASE_NUMBER].value == "2019형제20447"
    assert result.analysis.case_card.slots_done == 5
