"""3단계: 여러 자료의 Event를 시간축에 병합해 통합 타임라인을 만든다.

병합 규칙 (보수적)
- 같은 단계여야 한다
- 금액이 둘 다 있으면 같아야 하고, 시각이 둘 다 있으면 겹쳐야 한다
- 그 위에 '같은 일'이라는 근거가 하나 이상 있어야 한다:
  금액 일치 / 계좌·사건번호 같은 식별자 공유 / 하루 이하 입도로 시각이 겹침(발생 단계 제외)
금액이 다른 두 송금은 합치지 않는다 — 불일치 판단은 4단계가 출처와 함께 따로 한다.
"""

from __future__ import annotations

from datetime import datetime

from ..requirements import CaseRequirements
from ..schema import (
    EVIDENCE_RANK,
    GRANULARITY_RANK,
    STAGE_LABELS,
    EntityKind,
    Event,
    EvidenceLevel,
    ExtractionResult,
    SourceRef,
    Stage,
    StageState,
    StageStatus,
    TimeGap,
    TimeGranularity,
    Timeline,
    TimelineEvent,
)
from .coref import CoreferenceResolver

STRONG_IDS = {EntityKind.ACCOUNT, EntityKind.CASE_NUMBER, EntityKind.RECEIPT_NUMBER, EntityKind.PHONE}
STAGE_ORDER = list(Stage)


class TimelineBuilder:
    def __init__(self, coref: CoreferenceResolver | None = None):
        self.coref = coref or CoreferenceResolver()

    def build(self, extraction: ExtractionResult, requirements: CaseRequirements) -> Timeline:
        entities, mention_to_entity = self.coref.resolve(extraction.mentions)
        kind_of = {e.entity_id: e.kind for e in entities}

        def participants(ev: Event) -> set[str]:
            return {mention_to_entity[m] for m in ev.participant_mention_ids if m in mention_to_entity}

        def strong(ev: Event) -> set[str]:
            return {e for e in participants(ev) if kind_of[e] in STRONG_IDS}

        # 기록 자료, 정밀한 시각 순으로 먼저 자리를 잡게 한다
        ordered = sorted(
            extraction.events,
            key=lambda ev: (
                -EVIDENCE_RANK[ev.evidence_level],
                GRANULARITY_RANK[ev.time.value.granularity] if ev.time and ev.time.value.is_resolved else 99,
            ),
        )
        clusters: list[list[Event]] = []
        for ev in ordered:
            for cluster in clusters:
                if all(self._compatible(ev, other, strong) for other in cluster):
                    cluster.append(ev)
                    break
            else:
                clusters.append([ev])

        events = [self._to_timeline_event(n, c, participants) for n, c in enumerate(clusters, start=1)]
        events = self._order(events)
        stages, current = self._stage_status(events, requirements)
        return Timeline(
            case_type=requirements.case_type,
            events=events,
            stages=stages,
            current_stage=current,
            gaps=self._gaps(events, requirements.gap_threshold_hours),
            entities=entities,
            mention_to_entity=mention_to_entity,
        )

    @staticmethod
    def _compatible(a: Event, b: Event, strong) -> bool:
        if a.stage is not b.stage:
            return False
        if a.amount and b.amount and a.amount.value != b.amount.value:
            return False
        ta = a.time.value if a.time else None
        tb = b.time.value if b.time else None
        time_match = ta.compatible(tb) if ta and tb else None
        if time_match is False:
            return False
        evidence = bool(a.amount and b.amount) or bool(strong(a) & strong(b))
        if time_match and a.stage is not Stage.OCCURRENCE:
            evidence = evidence or (
                GRANULARITY_RANK[ta.granularity] <= GRANULARITY_RANK[TimeGranularity.DAY]  # type: ignore[union-attr]
                and GRANULARITY_RANK[tb.granularity] <= GRANULARITY_RANK[TimeGranularity.DAY]  # type: ignore[union-attr]
            )
        return evidence

    @staticmethod
    def _to_timeline_event(n: int, cluster: list[Event], participants) -> TimelineEvent:
        best_level = max((ev.evidence_level for ev in cluster), key=EVIDENCE_RANK.__getitem__)
        timed = [ev.time for ev in cluster if ev.time and ev.time.value.is_resolved]
        time = None
        if timed:
            time = min(
                timed,
                key=lambda t: (t.value.needs_confirmation, GRANULARITY_RANK[t.value.granularity], t.value.approximate,
                               -t.confidence),
            )
        amounts = [ev.amount for ev in cluster if ev.amount]
        amount = max(amounts, key=lambda a: a.confidence).value if amounts else None
        head = next(ev for ev in cluster if ev.evidence_level is best_level)
        stage = head.stage
        if amount is not None:
            title = f"{amount:,}원 {STAGE_LABELS[stage]}"
        else:
            quote = head.action.value
            title = quote if len(quote) <= 40 else quote[:39] + "…"

        sources: list[SourceRef] = []
        seen = set()
        for ev in cluster:
            for item in (ev.action, ev.time, ev.amount):
                if item is None:
                    continue
                key = (item.source_doc_id, item.source_line, item.char_start)
                if key not in seen:
                    seen.add(key)
                    sources.append(item.ref())

        flags = []
        if best_level is EvidenceLevel.STATEMENT:
            flags.append("claim_only")
        if best_level is EvidenceLevel.USER:
            flags.append("user_input")
        if len({ev.doc_id for ev in cluster}) > 1:
            flags.append("multi_source")
        needs = time is None or time.value.needs_confirmation
        return TimelineEvent(
            timeline_event_id=f"tl{n}",
            stage=stage,
            title=title,
            time=time.value if time else None,
            time_unknown=time is None,
            amount=amount,
            participant_entity_ids=sorted(set().union(*(participants(ev) for ev in cluster))),
            event_ids=[ev.event_id for ev in cluster],
            sources=sources,
            evidence_level=best_level,
            needs_confirmation=needs,
            flags=flags,
        )

    @staticmethod
    def _order(events: list[TimelineEvent]) -> list[TimelineEvent]:
        timed = sorted((e for e in events if e.time is not None), key=lambda e: e.time.start)  # type: ignore[union-attr]
        for ev in (e for e in events if e.time is None):
            idx = STAGE_ORDER.index(ev.stage)
            pos = 0
            for i, other in enumerate(timed):
                if STAGE_ORDER.index(other.stage) <= idx:
                    pos = i + 1
            timed.insert(pos, ev)
        return timed

    @staticmethod
    def _stage_status(
        events: list[TimelineEvent], requirements: CaseRequirements
    ) -> tuple[list[StageStatus], Stage | None]:
        flow = requirements.stages
        by_stage = {s: [e for e in events if e.stage is s] for s in flow}
        reached = [i for i, s in enumerate(flow) if by_stage[s]]
        current_idx = max(reached) if reached else None
        statuses = []
        for i, s in enumerate(flow):
            evs = by_stage[s]
            if current_idx is None or i > current_idx:
                state = StageState.PENDING
            elif i == current_idx:
                state = StageState.CURRENT
            else:
                state = StageState.DONE if evs else StageState.SKIPPED
            statuses.append(
                StageStatus(
                    stage=s,
                    label=STAGE_LABELS[s],
                    state=state,
                    timeline_event_ids=[e.timeline_event_id for e in evs],
                    evidence_level=max((e.evidence_level for e in evs), key=EVIDENCE_RANK.__getitem__) if evs else None,
                )
            )
        return statuses, flow[current_idx] if current_idx is not None else None

    @staticmethod
    def _gaps(events: list[TimelineEvent], threshold_hours: float | None) -> list[TimeGap]:
        if not threshold_hours:
            return []
        timed = [
            e for e in events
            if e.time is not None and GRANULARITY_RANK[e.time.granularity] <= GRANULARITY_RANK[TimeGranularity.DAY]
        ]
        gaps = []
        latest_end: datetime | None = None
        latest_id = None
        for ev in sorted(timed, key=lambda e: e.time.start):  # type: ignore[union-attr]
            start, end = ev.time.start, ev.time.end  # type: ignore[union-attr]
            if latest_end is not None and start > latest_end:
                hours = (start - latest_end).total_seconds() / 3600
                if hours > threshold_hours:
                    gaps.append(
                        TimeGap(start=latest_end, end=start, hours=round(hours, 1),
                                before_event_id=latest_id, after_event_id=ev.timeline_event_id)  # type: ignore[arg-type]
                    )
            if latest_end is None or end > latest_end:  # type: ignore[operator]
                latest_end, latest_id = end, ev.timeline_event_id
        return gaps
