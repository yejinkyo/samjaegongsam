import itertools
from datetime import datetime

from research_engine.requirements import load_requirements
from research_engine.schema import (
    EntityKind,
    EntityMention,
    Event,
    EvidenceLevel,
    ExtractionResult,
    Sourced,
    Stage,
    StageState,
    TimeGranularity,
    TimeValue,
)
from research_engine.timeline import CoreferenceResolver, TimelineBuilder, mask_compatible

_ids = itertools.count(1)
REQ = load_requirements("used_goods_fraud")


def mention(kind, text, normalized=None, role=None, doc="d1"):
    return EntityMention(
        mention_id=f"{doc}:m{next(_ids)}", doc_id=doc, kind=kind,
        name=Sourced[str](value=text, source_doc_id=doc, source_line=1, confidence=0.9),
        normalized=normalized or text, role=role,
    )


def event(stage, doc, start=None, end=None, amount=None, level=EvidenceLevel.RECORD, participants=(),
          granularity=TimeGranularity.MINUTE, line=1):
    time = None
    if start:
        time = Sourced[TimeValue](value=TimeValue(raw="t", start=start, end=end, granularity=granularity),
                                  source_doc_id=doc, source_line=line, confidence=0.9)
    return Event(
        event_id=f"{doc}:e{next(_ids)}", doc_id=doc, stage=stage,
        action=Sourced[str](value="행위", source_doc_id=doc, source_line=line, confidence=0.9),
        time=time,
        amount=Sourced[int](value=amount, source_doc_id=doc, source_line=line, confidence=0.9) if amount else None,
        participant_mention_ids=[p.mention_id for p in participants], evidence_level=level,
    )


def test_mask_compatible_requires_enough_visible_digits():
    assert mask_compatible("940*******21", "940123456721") == (True, 5)
    assert mask_compatible("9********1", "9123456781")[0] is False
    assert mask_compatible("940*******21", "110*******88")[0] is False


def test_coreference_merges_masked_account_and_role_consistent_names():
    ms = [
        mention(EntityKind.ACCOUNT, "940*-**-****21", "940*******21", doc="chat"),
        mention(EntityKind.ACCOUNT, "940123456721", doc="bank"),
        mention(EntityKind.PERSON, "김○○", "김**", role="피고인", doc="judgment"),
        mention(EntityKind.PERSON, "김철수", role="피고소인", doc="complaint"),
        mention(EntityKind.PERSON, "김철수", role="피해자", doc="news"),
    ]
    entities, m2e = CoreferenceResolver().resolve(ms)
    assert m2e[ms[0].mention_id] == m2e[ms[1].mention_id]
    assert m2e[ms[2].mention_id] == m2e[ms[3].mention_id]  # 피고인 ≈ 피고소인 + 마스킹 이름 호환
    victim = next(e for e in entities if ms[4].mention_id in e.mention_ids)
    assert victim.possible_same_as and "동명이인" in victim.possible_same_as[0].reason


def test_events_merge_only_with_evidence_and_never_with_different_amounts():
    acct_a = mention(EntityKind.ACCOUNT, "940*******21", doc="receipt")
    acct_b = mention(EntityKind.ACCOUNT, "940*******21", doc="chat")
    receipt = event(Stage.TRANSFER, "receipt", datetime(2026, 6, 1, 14, 5), datetime(2026, 6, 1, 14, 6), 350000,
                    participants=[acct_a])
    chat = event(Stage.TRANSFER, "chat", datetime(2026, 6, 1, 2, 5), datetime(2026, 6, 1, 14, 6),
                 level=EvidenceLevel.STATEMENT, participants=[acct_b])
    statement = event(Stage.TRANSFER, "st", datetime(2026, 6, 1, 13), datetime(2026, 6, 1, 16), 300000,
                      level=EvidenceLevel.STATEMENT)
    report = event(Stage.RECEIPT, "ecrm", datetime(2026, 6, 3, 9, 12), datetime(2026, 6, 3, 9, 13))
    ex = ExtractionResult(mentions=[acct_a, acct_b], events=[chat, statement, receipt, report])
    tl = TimelineBuilder().build(ex, REQ)

    transfer_events = [e for e in tl.events if e.stage is Stage.TRANSFER]
    assert len(transfer_events) == 2
    merged = next(e for e in transfer_events if e.amount == 350000)
    assert set(merged.event_ids) == {receipt.event_id, chat.event_id}
    assert merged.evidence_level is EvidenceLevel.RECORD and merged.time.start == datetime(2026, 6, 1, 14, 5)
    assert merged.title == "350,000원 송금" and "multi_source" in merged.flags
    assert {s.source_doc_id for s in merged.sources} == {"receipt", "chat"}


def test_stage_states_and_gaps():
    ex = ExtractionResult(events=[
        event(Stage.OCCURRENCE, "a", datetime(2026, 6, 1, 10), datetime(2026, 6, 1, 11)),
        event(Stage.RECEIPT, "b", datetime(2026, 6, 3, 9), datetime(2026, 6, 3, 10)),
    ])
    tl = TimelineBuilder().build(ex, REQ)
    states = {s.stage: s.state for s in tl.stages}
    assert states[Stage.OCCURRENCE] is StageState.DONE
    assert states[Stage.TRANSFER] is StageState.SKIPPED and states[Stage.REPORT] is StageState.SKIPPED
    assert states[Stage.RECEIPT] is StageState.CURRENT and states[Stage.OUTCOME] is StageState.PENDING
    assert tl.current_stage is Stage.RECEIPT
    [gap] = tl.gaps
    assert gap.start == datetime(2026, 6, 1, 11) and gap.end == datetime(2026, 6, 3, 9)


def test_untimed_event_placed_after_earlier_stages():
    ex = ExtractionResult(events=[
        event(Stage.TRANSFER, "a", datetime(2026, 6, 1, 10), datetime(2026, 6, 1, 11)),
        event(Stage.OUTCOME, "c", datetime(2026, 7, 1), datetime(2026, 7, 2), granularity=TimeGranularity.DAY),
        event(Stage.REPORT, "b"),
    ])
    tl = TimelineBuilder().build(ex, REQ)
    assert [e.stage for e in tl.events] == [Stage.TRANSFER, Stage.REPORT, Stage.OUTCOME]
    assert tl.events[1].time_unknown and tl.events[1].needs_confirmation


def test_document_dates_split_gaps_but_never_create_new_ones():
    points = [(datetime(2015, 10, 10), datetime(2015, 10, 11), "tl1"), (datetime(2022, 3, 15), datetime(2022, 3, 16), "tl2")]
    news = [(datetime(2016, 2, 3, 9, 10), datetime(2016, 2, 3, 9, 11), "doc:news")]
    late_doc = [(datetime(2024, 1, 1), datetime(2024, 1, 2), "doc:late")]
    gaps = TimelineBuilder._gaps(points, 8760, news + late_doc)
    assert [(g.before_event_id, g.after_event_id) for g in gaps] == [("doc:news", "tl2")]  # 2015→2016은 1년 미만
    assert gaps[0].start == datetime(2016, 2, 3, 9, 11)
