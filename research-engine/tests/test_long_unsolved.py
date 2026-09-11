"""장기 미제 실종 사건(2015 실종 → 2022 수사중지 → 2023 진정) 통합 테스트. 등장인물·사건은 가상이다."""

import pytest

from research_engine.pipeline import ResearchPipeline, load_case
from research_engine.schema import ClaimSlot, EvidenceLevel, GapCondition, IssueCategory, SlotState, Stage

from .conftest import FIXTURES


@pytest.fixture(scope="module")
def result():
    return ResearchPipeline().run(load_case(FIXTURES / "long_unsolved_missing" / "case.json"))


def test_notice_is_record_and_decision_is_current_stage(result):
    notice = next(d for d in result.documents if d.doc_id == "suspension_notice_2022")
    assert notice.doc_type.value == "notice" and notice.evidence_level is EvidenceLevel.RECORD
    assert result.timeline.current_stage is Stage.OUTCOME
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.DECISION_TYPE].state is SlotState.CONFIRMED
    assert slots[ClaimSlot.INVESTIGATOR].value == "박정호"
    assert slots[ClaimSlot.LAST_SEEN_TIME].state is SlotState.CONFIRMED  # 2015 접수증의 '최종 목격'


def test_later_sighting_flagged_as_unrecorded_fact(result):
    [issue] = [i for i in result.analysis.issues if i.condition is GapCondition.UNRECORDED_FACT]
    assert issue.category is IssueCategory.UNVERIFIED
    assert issue.trigger.key == "missing_person_suspended/occurrence/new_fact/unrecorded_fact"
    assert {s.source_doc_id for s in issue.sources} == {"witness_statement_2019", "petition_2023"}
    assert "수사중지 결정 통지서" in issue.message and "앞선" in issue.message
    assert issue.trigger.since.year == 2019


def test_elapsed_time_since_decision(result):
    stalled = next(i for i in result.analysis.issues if i.condition is GapCondition.STAGE_STALLED)
    assert stalled.trigger.stage is Stage.OUTCOME and stalled.trigger.elapsed_days == 1641


def test_no_false_contradictions_or_identity_links(result):
    assert not [i for i in result.analysis.issues if i.category is IssueCategory.INCONSISTENCY]
    assert not [i for i in result.analysis.issues if i.condition is GapCondition.IDENTITY_UNCONFIRMED]


def test_dates_resolved_from_context(result):
    memo_report = next(e for e in result.extraction.events if e.doc_id == "mother_memo" and e.stage is Stage.REPORT)
    assert memo_report.time.value.start.year == 2015
    petition = next(e for e in result.extraction.events if e.action_kind == "petition")
    assert petition.time.value.start.year == 2023


def test_gaps_respect_the_2016_news_article(result):
    starts = [g.start.year for g in result.timeline.gaps]
    assert 2015 not in starts and starts[0] == 2016
