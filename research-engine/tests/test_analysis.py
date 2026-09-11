import itertools
from datetime import date, datetime, timedelta

from research_engine.analysis import CaseAnalyzer, ConservativePolicy, SlotRuleNli, candidate_pairs
from research_engine.requirements import load_requirements
from research_engine.schema import (
    Claim,
    ClaimSlot,
    EvidenceLevel,
    ExtractionResult,
    GapCondition,
    IssueCategory,
    NliLabel,
    Polarity,
    Sourced,
    Stage,
    StageState,
    StageStatus,
    Timeline,
    TimeValue,
)

_ids = itertools.count(1)
REQ = load_requirements("used_goods_fraud")


def claim(slot, value, doc, conf=0.9, level=EvidenceLevel.RECORD, speaker="발급처", time=None, subject=None,
          self_value=False, polarity=Polarity.AFFIRM):
    return Claim(
        claim_id=f"{doc}:c{next(_ids)}", doc_id=doc, speaker=speaker, speaker_basis="document_issuer",
        content=Sourced[str](value=f"{slot.value}={value}", source_doc_id=doc, source_line=3, confidence=conf),
        slot=slot, slot_value=value, slot_time=time, subject=subject, value_is_speaker_self=self_value,
        polarity=polarity, evidence_level=level,
    )


def tv(start, end, approximate=False, needs=False):
    return TimeValue(raw="t", start=start, end=end, approximate=approximate, needs_confirmation=needs)


def timeline(current=Stage.RECEIPT):
    flow = REQ.stages
    idx = flow.index(current)
    stages = [StageStatus(stage=s, label=s.value, state=StageState.DONE if i < idx else
                          StageState.CURRENT if i == idx else StageState.PENDING) for i, s in enumerate(flow)]
    return Timeline(case_type=REQ.case_type, stages=stages, current_stage=current)


def analyze(claims):
    return CaseAnalyzer().analyze("c1", REQ, date(2026, 6, 24), [], ExtractionResult(claims=claims), timeline(), [])


def test_slot_rule_nli_amounts_and_names():
    nli = SlotRuleNli()
    a = claim(ClaimSlot.TRANSFER_AMOUNT, "350000", "receipt")
    b = claim(ClaimSlot.TRANSFER_AMOUNT, "300000", "statement")
    assert nli.score(a, b).argmax() is NliLabel.CONTRADICTION
    same = claim(ClaimSlot.TRANSFER_AMOUNT, "350000", "chat")
    assert nli.score(a, same).argmax() is NliLabel.ENTAILMENT
    nick = claim(ClaimSlot.ACCOUNT_HOLDER, "찬찬", "chat", self_value=True)
    real = claim(ClaimSlot.ACCOUNT_HOLDER, "이*민", "bank")
    assert nli.score(nick, real).argmax() is NliLabel.NEUTRAL  # 닉네임 vs 실명은 비교 불가


def test_confident_contradiction_becomes_inconsistency():
    t = tv(datetime(2026, 6, 1, 14, 5), datetime(2026, 6, 1, 14, 6))
    claims = [
        claim(ClaimSlot.TRANSFER_AMOUNT, "350000", "receipt"),
        claim(ClaimSlot.TRANSFER_TIME, "t", "receipt", time=t),
        claim(ClaimSlot.TRANSFER_AMOUNT, "300000", "statement", level=EvidenceLevel.STATEMENT, speaker="홍길동"),
        claim(ClaimSlot.TRANSFER_TIME, "t", "statement", time=tv(datetime(2026, 6, 1, 13), datetime(2026, 6, 1, 16), True),
              level=EvidenceLevel.STATEMENT),
    ]
    result = analyze(claims)
    [issue] = [i for i in result.issues if i.category is IssueCategory.INCONSISTENCY]
    assert issue.slot is ClaimSlot.TRANSFER_AMOUNT and issue.priority == 10
    assert {s.source_doc_id for s in issue.sources} == {"receipt", "statement"}
    assert "350,000원" in issue.message and "300,000원" in issue.message
    assert issue.trigger.key == "used_goods_fraud/transfer/transfer_amount/conflicting"
    assert result.case_card.next_trigger.key == issue.trigger.key


def test_low_confidence_contradiction_is_downgraded_to_neutral():
    t = tv(datetime(2026, 6, 1, 14, 5), datetime(2026, 6, 1, 14, 6))
    claims = [
        claim(ClaimSlot.TRANSFER_AMOUNT, "350000", "receipt"),
        claim(ClaimSlot.TRANSFER_TIME, "t", "receipt", time=t),
        claim(ClaimSlot.TRANSFER_AMOUNT, "300000", "memo", conf=0.55, level=EvidenceLevel.STATEMENT),
        claim(ClaimSlot.TRANSFER_TIME, "t", "memo", conf=0.55, time=t, level=EvidenceLevel.STATEMENT),
    ]
    result = analyze(claims)
    assert not [i for i in result.issues if i.category is IssueCategory.INCONSISTENCY]
    [suspect] = [i for i in result.issues if i.condition is GapCondition.SUSPECTED_CONFLICT]
    assert suspect.category is IssueCategory.UNVERIFIED
    assert suspect.decision.model_label is NliLabel.CONTRADICTION and suspect.decision.label is NliLabel.NEUTRAL
    assert any("신뢰도" in r for r in suspect.decision.reasons)
    status = next(s for s in result.slot_statuses if s.slot is ClaimSlot.TRANSFER_AMOUNT)
    assert status.value == "350,000원"


def test_uncertain_subject_blocks_contradiction():
    policy = ConservativePolicy()
    a = claim(ClaimSlot.TRANSFER_AMOUNT, "350000", "receipt")
    b = claim(ClaimSlot.TRANSFER_AMOUNT, "50000", "chat")
    scores = SlotRuleNli().score(a, b)
    decision = policy.decide("p", a, b, scores, "rule", subject_certain=False)
    assert decision.label is NliLabel.NEUTRAL and decision.downgraded


def test_pairing_skips_same_document_and_different_accounts():
    claims = [
        claim(ClaimSlot.ACCOUNT_NUMBER, "110*******88", "receipt", subject="withdrawal"),
        claim(ClaimSlot.ACCOUNT_NUMBER, "940*******21", "receipt", subject="deposit"),
        claim(ClaimSlot.ACCOUNT_NUMBER, "940*******21", "chat", subject="deposit"),
    ]
    pairs = candidate_pairs(ExtractionResult(claims=claims))
    assert [(p.a.slot_value, p.b.slot_value) for p in pairs] == [("940*******21", "940*******21")]


def test_claim_only_and_missing_slots_feed_action_triggers():
    claims = [
        claim(ClaimSlot.ACCOUNT_HOLDER, "찬찬", "chat", level=EvidenceLevel.STATEMENT, speaker="찬찬", self_value=True),
        claim(ClaimSlot.RECEIPT_NUMBER, "2026-0603-***", "ecrm"),
    ]
    result = analyze(claims)
    by_slot = {s.slot: s.state.value for s in result.slot_statuses}
    assert by_slot[ClaimSlot.ACCOUNT_HOLDER] == "claimed_only"
    assert by_slot[ClaimSlot.RECEIPT_NUMBER] == "confirmed"
    assert by_slot[ClaimSlot.INVESTIGATOR] == "missing"  # 다음 단계(수사) 항목까지 본다
    assert ClaimSlot.SHIPMENT_SENT in by_slot and not any(
        i.slot is ClaimSlot.SHIPMENT_SENT for i in result.issues)  # 선택 항목은 없어도 '빠짐' 아님
    keys = [t.key for t in result.action_triggers]
    assert "used_goods_fraud/transfer/account_holder/claimed_only" in keys
    assert "used_goods_fraud/investigation/investigator/missing" in keys
    holder_issue = next(i for i in result.issues if i.slot is ClaimSlot.ACCOUNT_HOLDER)
    assert holder_issue.category is IssueCategory.UNVERIFIED and holder_issue.sources[0].source_doc_id == "chat"


def _dated(c, doc_date):
    value = tv(doc_date, doc_date + timedelta(days=1))
    return {c.doc_id: Sourced[TimeValue](value=value, source_doc_id=c.doc_id, source_line=1, confidence=0.9)}


def test_value_changed_after_record_becomes_outdated_not_confirmed():
    record = claim(ClaimSlot.INVESTIGATOR, "박정호", "notice")
    change = claim(ClaimSlot.INVESTIGATOR_CHANGE, "changed", "memo", conf=0.6, level=EvidenceLevel.STATEMENT,
                   time=tv(datetime(2025, 10, 4), datetime(2025, 10, 9), approximate=True))
    ex = ExtractionResult(claims=[record, change], document_dates=_dated(record, datetime(2022, 3, 15)))
    result = CaseAnalyzer().analyze("c1", REQ, date(2026, 9, 11), [], ex, timeline(Stage.RECEIPT), [])
    status = next(s for s in result.slot_statuses if s.slot is ClaimSlot.INVESTIGATOR)
    assert status.state.value == "outdated" and status.value == "박정호"
    issue = next(i for i in result.issues if i.slot is ClaimSlot.INVESTIGATOR)
    assert issue.condition is GapCondition.POSSIBLY_OUTDATED and issue.category is IssueCategory.UNVERIFIED
    assert issue.trigger.key == "used_goods_fraud/investigation/investigator/possibly_outdated"
    assert {s.source_doc_id for s in issue.sources} == {"notice", "memo"}


def test_record_issued_after_the_change_is_confirmed_and_not_compared_with_old_value():
    change = claim(ClaimSlot.INVESTIGATOR_CHANGE, "changed", "memo", level=EvidenceLevel.STATEMENT,
                   time=tv(datetime(2023, 1, 1), datetime(2023, 1, 2)))
    old = claim(ClaimSlot.INVESTIGATOR, "박정호", "notice2022", time=tv(datetime(2022, 3, 15), datetime(2022, 3, 16)))
    new = claim(ClaimSlot.INVESTIGATOR, "김영수", "notice2024", time=tv(datetime(2024, 5, 1), datetime(2024, 5, 2)))
    result = analyze([change, old, new])
    status = next(s for s in result.slot_statuses if s.slot is ClaimSlot.INVESTIGATOR)
    assert status.state.value == "confirmed" and status.value == "김영수"
    assert not [i for i in result.issues if i.category is IssueCategory.INCONSISTENCY]
    assert not [d for d in result.pair_decisions if d.slot is ClaimSlot.INVESTIGATOR]
