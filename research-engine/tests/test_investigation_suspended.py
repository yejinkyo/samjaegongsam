"""수사중지 사건(2021 고소 → 2023 참고인중지 → 2025 목격 제보) 통합 테스트. 등장인물·사건은 가상이다.

``missing_person_suspended``와 달리 발생 단계 항목이 ``incident_time``이고 실종 서식이 없는
일반 수사중지 유형이다 (proposal.md §10 파일럿 유형).
"""

import pytest

from research_engine.pipeline import ResearchPipeline, load_case
from research_engine.schema import ClaimSlot, EntityKind, EvidenceLevel, GapCondition, IssueCategory, SlotState, Stage

from .conftest import FIXTURES


@pytest.fixture(scope="module")
def result():
    return ResearchPipeline().run(load_case(FIXTURES / "investigation_suspended" / "case.json"))


def test_결정_통지서가_기록으로_읽히고_결정_항목을_채운다(result):
    notice = next(d for d in result.documents if d.doc_id == "suspension_notice_2023")
    assert notice.doc_type.value == "notice" and notice.evidence_level is EvidenceLevel.RECORD
    assert result.timeline.current_stage is Stage.OUTCOME
    slots = {s.slot: s for s in result.analysis.slot_statuses}
    assert slots[ClaimSlot.DECISION_TYPE].state is SlotState.CONFIRMED
    assert slots[ClaimSlot.DECISION_TIME].value == "2023-02-09"
    assert slots[ClaimSlot.CASE_NUMBER].value == "2021형제45678"
    assert slots[ClaimSlot.INVESTIGATOR].value == "한지훈"
    assert slots[ClaimSlot.RECEIPT_NUMBER].value == "2021-005821"  # 접수증(기록)에서 온 값
    assert result.analysis.case_card.slots_done == 3  # 필수 4개 중 사건 발생 시점만 기록으로 확인되지 않음


def test_중지_사유가_항목_값까지_올라온다(result):
    """결정 종류는 제목이 아니라 결정내용란에서 온다.

    실제 서식(경찰수사규칙 별지 제100호 ‘수사결과 통지서’)은 제목에 결정 종류를 적지 않는다.
    수사중지인지 송치인지는 결정내용란에만 있고, 행동 강령 엔진은 이 값으로
    피의자중지·참고인중지를 가른다. 사유가 붙은 값이 그대로 항목 값이 되어야 한다.

    한 항목에 기록 여러 줄이 걸릴 때 더 구체적인 값을 세우는 규칙 자체는
    ``test_analysis.py`` 가 따로 덮는다 — 이 픽스처에서는 겹치는 줄이 생기지 않는다.
    """
    values = [c.slot_value for c in result.extraction.claims if c.slot is ClaimSlot.DECISION_TYPE]
    assert values == ["수사중지(참고인중지)"]
    status = next(s for s in result.analysis.slot_statuses if s.slot is ClaimSlot.DECISION_TYPE)
    assert status.value == "수사중지(참고인중지)"
    assert status.sources[0].source_line == 7  # 제목(1줄)이 아니라 결정내용란


def test_중지_이후의_목격_진술이_기록에_없는_사실로_올라온다(result):
    [issue] = [i for i in result.analysis.issues if i.condition is GapCondition.UNRECORDED_FACT]
    assert issue.category is IssueCategory.UNVERIFIED
    assert issue.trigger.key == "investigation_suspended/occurrence/new_fact/unrecorded_fact"
    assert {s.source_doc_id for s in issue.sources} == {"witness_statement_2025"}
    assert "수사결과 통지서" in issue.message and "이후에 나온 내용" in issue.message
    assert issue.trigger.since.year == 2025
    assert result.analysis.case_card.next_trigger.key == issue.trigger.key  # 가장 먼저 다룰 것


def test_결정_이후_경과일을_결정일부터_센다(result):
    stalled = next(i for i in result.analysis.issues if i.condition is GapCondition.STAGE_STALLED)
    assert stalled.trigger.stage is Stage.OUTCOME and stalled.trigger.elapsed_days == 1311
    assert stalled.trigger.since.date().isoformat() == "2023-02-09"


def test_수사_단계_자료가_없으면_빠진_단계로_표시한다(result):
    states = {st.stage: st.state for st in result.timeline.stages}
    assert states[Stage.INVESTIGATION].value == "skipped"  # 접수증과 결정 통지서 사이가 비어 있다
    skipped = next(i for i in result.analysis.issues if i.condition is GapCondition.STAGE_SKIPPED)
    assert skipped.stage is Stage.INVESTIGATION


def test_사건_발생_시점은_진술뿐이라_확인_대상이다(result):
    status = next(s for s in result.analysis.slot_statuses if s.slot is ClaimSlot.INCIDENT_TIME)
    assert status.state is SlotState.CLAIMED_ONLY  # 고소장·진술서에만 있고 기록 자료에는 없다
    issue = next(i for i in result.analysis.issues if i.slot is ClaimSlot.INCIDENT_TIME)
    assert "2021. 5. 18." in issue.message
    # 2025년 목격 진술도 같은 발생 단계라 이 항목에 함께 묶인다 — 목격 시점과 발생 시점은 다르다
    assert {s.source_doc_id for s in issue.sources} == {"complaint_2021", "witness_statement_2025"}


def test_기록이_비어_있는_구간을_연_단위로_묶는다(result):
    assert [(g.start.date().isoformat(), g.end.date().isoformat()) for g in result.timeline.gaps] == [
        ("2021-05-26", "2023-02-09"),  # 접수 후 결정까지
        ("2023-02-10", "2025-06-03"),  # 결정 후 목격 제보까지
    ]


def test_통지서_사유란을_사람_이름으로_읽지_않는다(result):
    """‘참고인 소재불명으로’ 의 뒷말이 참고인 이름으로 잡히던 문제."""
    people = {e.canonical_name for e in result.timeline.entities if e.kind is EntityKind.PERSON}
    assert people == {"정하늘", "한지훈", "조미래"}


def test_없는_모순과_동일인_의심을_만들지_않는다(result):
    assert not [i for i in result.analysis.issues if i.category is IssueCategory.INCONSISTENCY]
    assert not [i for i in result.analysis.issues if i.condition is GapCondition.IDENTITY_UNCONFIRMED]
