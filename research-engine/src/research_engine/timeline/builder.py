"""3단계: 여러 자료의 Event를 시간축에 병합해 통합 타임라인을 만든다.

병합 규칙 (보수적)
- 같은 단계여야 한다
- 금액이 둘 다 있으면 같아야 하고, 시각이 둘 다 있으면 겹쳐야 한다
- 그 위에 '같은 일'이라는 근거가 하나 이상 있어야 한다:
  금액 일치 / 계좌·사건번호 같은 식별자 공유 / 하루 이하 입도로 시각이 겹침(발생 단계 제외)
금액이 다른 두 송금은 합치지 않는다 — 불일치 판단은 4단계가 출처와 함께 따로 한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta

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
        # 공백 계산에는 합쳐진 이벤트의 대표 시각만이 아니라 구성 이벤트 각각의 시각을 모두 쓴다
        event_points = [
            (ev.time.value.start, ev.time.value.end, tl.timeline_event_id)
            for tl, cluster in zip(events, clusters, strict=True)
            for ev in cluster
            if ev.time is not None and ev.time.value.is_resolved
        ]
        events = self._order(events)
        stages, current = self._stage_status(events, requirements)
        return Timeline(
            case_type=requirements.case_type,
            events=events,
            stages=stages,
            current_stage=current,
            gaps=self._gaps(
                event_points,
                requirements.gap_threshold_hours,
                # 문서 자체의 작성·발행일도 '그 시점에 기록이 있었다'는 근거다 (예: 2016년 보도)
                [(d.value.start, d.value.end, f"doc:{doc_id}") for doc_id, d in extraction.document_dates.items()
                 if d.value.is_resolved],
            ),
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
        if time_match and a.stage is Stage.OCCURRENCE:
            # 발생 단계는 여러 일이 섞이므로 같은 종류의 행위(목격끼리, 연락 두절끼리)일 때만 합친다
            evidence = evidence or (a.action_kind is not None and a.action_kind == b.action_kind)
        return evidence

    @staticmethod
    def _to_timeline_event(n: int, cluster: list[Event], participants) -> TimelineEvent:
        best_level = max((ev.evidence_level for ev in cluster), key=EVIDENCE_RANK.__getitem__)
        timed = [ev.time for ev in cluster if ev.time and ev.time.value.is_resolved]
        time = None
        if timed:
            time = min(
                timed,
                key=lambda t: (t.value.needs_confirmation, GRANULARITY_RANK[t.value.granularity],
                               t.value.end - t.value.start, t.value.approximate, -t.confidence),
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
        if stage is Stage.OCCURRENCE and all(ev.action_kind is None for ev in cluster):
            # 단서가 없어 '발생'에 둔 메모 (extract/events.py) — 무슨 단계의 일인지 모른다
            flags.append("stage_guessed")
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
        # 사용자가 적은 메모는 그 단계의 '자료'로 세지 않는다. 메모는 자료가 아니다 —
        # 직접 적었다고 '그 단계 자료가 있다'가 되면, 빠진 자료를 찾아 주는 일이 무너진다.
        # (단계의 근거 이벤트 · 증거 수준에는 넣지 않는다.)
        #
        # 하지만 사건이 어디까지 왔는지는 메모로도 알 수 있다. 자료 없이 기억나는 일만 적은 사건에서
        # 메모를 빼 버리면 진행 단계가 영영 비어 있다. 그래서 '지금 단계'는 메모까지 보고 정하고,
        # 메모로만 이른 단계는 noted_only 로 표시한다.
        counted = [e for e in events if e.evidence_level is not EvidenceLevel.USER]
        by_stage = {s: [e for e in counted if e.stage is s] for s in flow}
        # 단서가 없어 '발생'에 놓인 메모('통지서가 번졌습니다')는 어느 단계의 일인지 모르므로 세지 않는다
        noted = {s for s in flow if any(e.stage is s and e.evidence_level is EvidenceLevel.USER
                                        and "stage_guessed" not in e.flags for e in events)}
        reached = [i for i, s in enumerate(flow) if by_stage[s] or s in noted]
        current_idx = max(reached) if reached else None
        statuses = []
        for i, s in enumerate(flow):
            evs = by_stage[s]
            if current_idx is None or i > current_idx:
                state = StageState.PENDING
            elif i == current_idx:
                state = StageState.CURRENT
            else:
                state = StageState.DONE if evs or s in noted else StageState.SKIPPED
            statuses.append(
                StageStatus(
                    stage=s,
                    label=STAGE_LABELS[s],
                    state=state,
                    timeline_event_ids=[e.timeline_event_id for e in evs],
                    evidence_level=max((e.evidence_level for e in evs), key=EVIDENCE_RANK.__getitem__) if evs else None,
                    noted_only=not evs and s in noted and state is not StageState.PENDING,
                )
            )
        return statuses, flow[current_idx] if current_idx is not None else None

    @staticmethod
    def _gaps(
        event_points: list[tuple[datetime, datetime, str]],
        threshold_hours: float | None,
        doc_points: list[tuple[datetime, datetime, str]] | None = None,
    ) -> list[TimeGap]:
        """기록 공백. 점은 (시작, 끝, 타임라인 이벤트 id 또는 'doc:{문서 id}').

        공백은 이벤트 사이에서만 찾고, 문서 작성·발행일은 그 공백을 나누는 데만 쓴다
        (사건 뒤에 쓴 진술서가 새 공백을 만들지 않도록).
        """
        if not threshold_hours:
            return []
        threshold = timedelta(hours=threshold_hours)
        # 공백 기준보다 충분히 짧은 구간만 '그때 기록이 있다'로 친다 (장기 사건은 '2019년 3월 초순'도 포함)
        max_span = timedelta(hours=max(24.0, threshold_hours / 2))
        points = sorted(p for p in event_points if p[1] - p[0] <= max_span)
        docs = sorted(p for p in (doc_points or []) if p[1] - p[0] <= max_span)

        spans: list[tuple[datetime, datetime, str, str]] = []
        latest_end: datetime | None = None
        latest_id = ""
        for start, end, point_id in points:
            if latest_end is not None and start - latest_end > threshold:
                spans.append((latest_end, start, latest_id, point_id))
            if latest_end is None or end > latest_end:
                latest_end, latest_id = end, point_id

        gaps = []
        for g_start, g_end, before, after in spans:
            cursor, cursor_id = g_start, before
            for d_start, d_end, doc_id in docs:
                if g_start < d_start and d_end <= g_end:
                    if d_start - cursor > threshold:
                        gaps.append((cursor, d_start, cursor_id, doc_id))
                    cursor, cursor_id = max(cursor, d_end), doc_id
            if g_end - cursor > threshold:
                gaps.append((cursor, g_end, cursor_id, after))
        return [
            TimeGap(start=s, end=e, hours=round((e - s).total_seconds() / 3600, 1), before_event_id=b, after_event_id=a)
            for s, e, b, a in gaps
        ]
