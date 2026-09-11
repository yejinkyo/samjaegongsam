"""4단계 오케스트레이션: 모순·공백 탐지 → Issue / ActionTrigger / CaseCard.

문구는 추출된 값과 원문 인용만으로 만든다. 절차(무엇을 어디에 내라)는 여기서 만들지 않는다 —
그건 ``ActionTrigger.key``를 받아 검증된 지식베이스를 조회하는 행동 강령 엔진의 몫이다.
"""

from __future__ import annotations

from datetime import date
from itertools import count

from ..requirements import CaseRequirements
from ..schema import (
    ActionTrigger,
    CaseAnalysis,
    CaseCard,
    Claim,
    ClaimSlot,
    ClarificationKind,
    ClarificationRequest,
    DocumentType,
    EntityKind,
    EvidenceLevel,
    ExtractionResult,
    GapCondition,
    Issue,
    IssueCategory,
    NliLabel,
    PairDecision,
    ProcessedDocument,
    SlotState,
    SourceRef,
    Stage,
    StageState,
    Timeline,
    TimelineEvent,
)
from .nli import CombinedNli, NliModel
from .pairing import candidate_pairs
from .policy import ConservativePolicy
from .slots import display_value, evaluate_slots

C = GapCondition
PRIORITY = {
    C.CONFLICTING: 10,
    C.UNREADABLE: 20,
    C.UNRECORDED_FACT: 25,
    C.MISSING: 30,
    C.STAGE_STALLED: 35,
    C.STAGE_SKIPPED: 45,
    C.CLAIMED_ONLY: 50,
    C.SUSPECTED_CONFLICT: 50,
    C.LOW_CONFIDENCE: 55,
    C.IDENTITY_UNCONFIRMED: 60,
    C.TIME_GAP: 70,
}
SLOT_STATE_ISSUE = {
    SlotState.CLAIMED_ONLY: (IssueCategory.UNVERIFIED, C.CLAIMED_ONLY),
    SlotState.LOW_CONFIDENCE: (IssueCategory.UNVERIFIED, C.LOW_CONFIDENCE),
    SlotState.MISSING: (IssueCategory.MISSING, C.MISSING),
    SlotState.UNREADABLE: (IssueCategory.UNREADABLE, C.UNREADABLE),
}


IDENTITY_SILENT_KINDS = {EntityKind.ORGANIZATION, EntityKind.PLACE}


def trigger_key(case_type: str, stage: Stage | None, subject: str, condition: GapCondition) -> str:
    return f"{case_type}/{stage.value if stage else '-'}/{subject}/{condition.value}"


class CaseAnalyzer:
    def __init__(
        self,
        nli: NliModel | None = None,
        policy: ConservativePolicy | None = None,
        min_slot_confidence: float | None = None,
    ):
        self.nli = nli or CombinedNli()
        self.policy = policy or ConservativePolicy()
        self.min_slot_confidence = (
            min_slot_confidence if min_slot_confidence is not None else self.policy.min_claim_confidence
        )

    def analyze(
        self,
        case_id: str,
        requirements: CaseRequirements,
        as_of: date,
        docs: list[ProcessedDocument],
        extraction: ExtractionResult,
        timeline: Timeline,
        clarifications: list[ClarificationRequest],
    ) -> CaseAnalysis:
        claims = {c.claim_id: c for c in extraction.claims}
        decisions = self._decide(extraction, timeline)
        slots = evaluate_slots(requirements, extraction.claims, decisions, docs, timeline, self.min_slot_confidence)
        ct = requirements.case_type
        issues: list[Issue] = []
        current_idx = (
            requirements.stages.index(timeline.current_stage) if timeline.current_stage in requirements.stages else -1
        )

        def add(category, condition, message, *, stage=None, slot=None, sources=(), checked=(), claim_ids=(),
                event_ids=(), entity_ids=(), q_ids=(), decision=None, subject=None, since=None, elapsed=None):
            subject_key = subject or (slot.value if slot else condition.value)
            priority = PRIORITY[condition]
            if stage in requirements.stages and requirements.stages.index(stage) > current_idx:
                priority += 10  # 다음 단계 항목은 현재 단계 항목보다 뒤
            issues.append(
                Issue(
                    issue_id="",
                    category=category,
                    condition=condition,
                    message=message,
                    stage=stage,
                    slot=slot,
                    sources=list(sources),
                    checked_doc_ids=list(checked),
                    related_claim_ids=list(claim_ids),
                    related_event_ids=list(event_ids),
                    related_entity_ids=list(entity_ids),
                    clarification_request_ids=list(q_ids),
                    decision=decision,
                    trigger=ActionTrigger(
                        key=trigger_key(ct, stage, subject_key, condition),
                        case_type=ct,
                        condition=condition,
                        stage=stage,
                        slot=slot,
                        since=since,
                        elapsed_days=elapsed,
                        evidence=list(sources),
                    ),
                    priority=priority,
                )
            )

        slot_stage = {s.slot: s.stage for s in requirements.slots}
        slot_label = {s.slot: s.label for s in requirements.slots}
        checked_docs = [d.doc_id for d in docs]

        # 1) 자료 간 불일치 (확정) — 슬롯별로 묶는다
        confirmed = [d for d in decisions if d.label is NliLabel.CONTRADICTION]
        for slot, group in _group_by_slot(confirmed).items():
            involved = _claims_of(group, claims)
            values = " / ".join(f"‘{display_value(c)}’({c.content.cite()})" for c in _distinct_values(involved))
            label = slot_label.get(slot, slot.value if slot else "주장")
            add(IssueCategory.INCONSISTENCY, C.CONFLICTING, f"{label}: 자료마다 다르게 적혀 있습니다 — {values}",
                stage=slot_stage.get(slot), slot=slot, sources=[c.content.ref() for c in involved],
                claim_ids=[c.claim_id for c in involved], decision=max(group, key=lambda d: d.scores.contradiction))

        # 2) 차이 의심 (Neutral로 내림) — 확정 불일치가 없는 슬롯만
        suspected = [d for d in decisions if self.policy.is_suspected(d) and d.slot not in {x.slot for x in confirmed}]
        for slot, group in _group_by_slot(suspected).items():
            involved = _claims_of(group, claims)
            top = max(group, key=lambda d: d.scores.contradiction)
            values = " / ".join(f"‘{display_value(c)}’({c.content.cite()})" for c in _distinct_values(involved))
            label = slot_label.get(slot, slot.value if slot else "주장")
            add(IssueCategory.UNVERIFIED, C.SUSPECTED_CONFLICT,
                f"{label}: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — {values} ({'; '.join(top.reasons)})",
                stage=slot_stage.get(slot), slot=slot, sources=[c.content.ref() for c in involved],
                claim_ids=[c.claim_id for c in involved], decision=top)

        # 3) 슬롯 상태
        for st in slots:
            if st.state not in SLOT_STATE_ISSUE or (st.state is SlotState.MISSING and not st.required):
                continue
            category, condition = SLOT_STATE_ISSUE[st.state]
            if st.state is SlotState.CLAIMED_ONLY:
                speakers = sorted({claims[cid].speaker for cid in st.claim_ids})
                quotes = " / ".join(f"‘{claims[cid].content.value}’({claims[cid].content.cite()})" for cid in st.claim_ids[:3])
                msg = f"{st.label}: {', '.join(speakers)}의 말만 있고 이를 뒷받침하는 기록 자료가 없습니다 — {quotes}"
            elif st.state is SlotState.LOW_CONFIDENCE:
                values = " / ".join(
                    f"‘{display_value(claims[cid])}’({claims[cid].content.cite()})" for cid in st.claim_ids[:3]
                )
                msg = f"{st.label}: {values} — 자료에서 읽어낸 값의 신뢰도가 낮아 확인이 필요합니다"
            elif st.state is SlotState.UNREADABLE:
                msg = f"{st.label}: 올린 자료에서 찾지 못했고, 해당 내용이 있을 수 있는 부분이 읽히지 않았습니다"
            else:
                msg = f"{st.label}: 올린 자료에서 찾지 못했습니다"
            add(category, condition, msg, stage=st.stage, slot=st.slot, sources=st.sources,
                checked=checked_docs if st.state in (SlotState.MISSING, SlotState.UNREADABLE) else (),
                claim_ids=st.claim_ids)

        # 4) 읽히지 않은 부분 — 문서별 1건, 질문은 줄마다
        q_by_line = {(q.doc_id, q.line_no): q.request_id for q in clarifications
                     if q.kind is ClarificationKind.UNREADABLE_TEXT and q.status == "pending"}
        for d in docs:
            if not d.unreadable:
                continue
            refs = [SourceRef(source_doc_id=u.doc_id, page=u.page, source_line=u.line_no, source_bbox=u.bbox)
                    for u in d.unreadable]
            lines = ", ".join(str(u.line_no) for u in d.unreadable)
            add(IssueCategory.UNREADABLE, C.UNREADABLE,
                f"{d.file_name}에서 읽히지 않은 부분이 {len(d.unreadable)}곳 있습니다 ({lines}줄). 사진을 보고 알려주세요",
                sources=refs, q_ids=[q_by_line[(d.doc_id, u.line_no)] for u in d.unreadable
                                     if (d.doc_id, u.line_no) in q_by_line],
                subject=f"document:{d.doc_type.value}")

        # 5) 날짜 확정 불가 (오탈자 후보)
        for q in clarifications + extraction.clarifications:
            if q.kind is ClarificationKind.AMBIGUOUS_DATE and q.status == "pending":
                ref = SourceRef(source_doc_id=q.doc_id, page=q.page, source_line=q.line_no, source_bbox=q.bbox,
                                quote=q.context[0] if q.context else None)
                add(IssueCategory.UNVERIFIED, C.LOW_CONFIDENCE,
                    f"‘{q.context[0] if q.context else ''}’({ref.cite()}) 날짜를 확정할 수 없습니다",
                    sources=[ref], q_ids=[q.request_id], subject="date")

        # 6) 동일인·동일 대상 여부 (기관 명칭 차이는 사건 판단에 영향이 작아 목록에 올리지 않는다)
        by_id = {e.entity_id: e for e in timeline.entities}
        seen = set()
        for e in timeline.entities:
            if e.kind in IDENTITY_SILENT_KINDS:
                continue
            for link in e.possible_same_as:
                key = tuple(sorted((e.entity_id, link.other_entity_id)))
                if key in seen:
                    continue
                seen.add(key)
                other = by_id[link.other_entity_id]
                add(IssueCategory.UNVERIFIED, C.IDENTITY_UNCONFIRMED,
                    f"‘{e.canonical_name}’과(와) ‘{other.canonical_name}’이(가) 같은 대상인지 확인되지 않았습니다 ({link.reason})",
                    sources=e.sources[:1] + other.sources[:1], entity_ids=list(key), subject=f"identity:{e.kind.value}")

        # 7) 타임라인 공백·단계
        events = {ev.timeline_event_id: ev for ev in timeline.events}
        def point_sources(point_id: str) -> list[SourceRef]:
            if point_id.startswith("doc:"):
                doc_date = extraction.document_dates.get(point_id[4:])
                return [doc_date.ref()] if doc_date else []
            return events[point_id].sources[:1] if point_id in events else []

        for gap in timeline.gaps:
            fmt = "%m/%d %H:%M" if gap.start.year == gap.end.year else "%Y-%m-%d"
            add(IssueCategory.MISSING, C.TIME_GAP,
                f"{gap.start:{fmt}} ~ {gap.end:{fmt}} 사이의 기록이 없습니다 (약 {_span_label(gap.hours)})",
                sources=point_sources(gap.before_event_id) + point_sources(gap.after_event_id), checked=checked_docs,
                event_ids=[p for p in (gap.before_event_id, gap.after_event_id) if p in events], subject="timeline")
        for st in timeline.stages:
            if st.state is StageState.SKIPPED:
                add(IssueCategory.MISSING, C.STAGE_SKIPPED, f"‘{st.label}’ 단계에 해당하는 자료가 없습니다",
                    stage=st.stage, checked=checked_docs, subject="stage")
        stalled = self._stall(timeline, requirements, as_of)
        if stalled is not None:
            stage, last_ev, since, days = stalled
            who = "기관의 " if last_ev.evidence_level is EvidenceLevel.RECORD else ""
            add(IssueCategory.MISSING, C.STAGE_STALLED,
                f"‘{last_ev.title}’({last_ev.time.iso()}) 이후 {who}진행 기록이 없습니다 ({days}일 경과)",  # type: ignore[union-attr]
                stage=stage, sources=last_ev.sources[:1], checked=checked_docs,
                event_ids=[last_ev.timeline_event_id], subject="stage", since=since, elapsed=days)

        # 8) 사건 이후에 나왔지만 기록 자료로 확인되지 않는 사실 — 재수사 요청의 '새로 확인된 사실' 후보
        if requirements.flag_unrecorded_facts:
            for ev, decision in _unrecorded_facts(timeline):
                cites = ", ".join(dict.fromkeys(s.cite() for s in ev.sources))
                when = ev.time.iso() if ev.time else "시점 미상"  # type: ignore[union-attr]
                relation = ""
                if decision is not None and decision.time is not None and ev.time is not None:
                    d_when = decision.time.iso()
                    relation = (f" ‘{decision.title}’({d_when})보다 앞선 내용입니다." if ev.time.end <= decision.time.start
                                else f" ‘{decision.title}’({d_when}) 이후에 나온 내용입니다.")
                add(IssueCategory.UNVERIFIED, C.UNRECORDED_FACT,
                    f"‘{ev.title}’({when}, {cites}) — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다."
                    f"{relation} 수사 기록에 반영됐는지 확인이 필요합니다",
                    stage=ev.stage, sources=ev.sources, checked=checked_docs, event_ids=[ev.timeline_event_id],
                    subject="new_fact", since=ev.time.start if ev.time else None)

        issues.sort(key=lambda i: (i.priority, i.stage and requirements.stages.index(i.stage)
                                   if i.stage in requirements.stages else 99))
        for n, issue in enumerate(issues, start=1):
            issue.issue_id = f"iss{n}"

        triggers: list[ActionTrigger] = []
        seen_keys = set()
        for issue in issues:
            if issue.trigger.key not in seen_keys:
                seen_keys.add(issue.trigger.key)
                triggers.append(issue.trigger)

        required = [s for s in slots if s.required]
        card = CaseCard(
            case_type=ct,
            case_type_label=requirements.label,
            requirements_status=requirements.status,
            stages=timeline.stages,
            current_stage=timeline.current_stage,
            evidence_doc_count=sum(1 for d in docs if d.doc_type is not DocumentType.USER_NOTE),
            needs_confirmation_count=len(issues),
            slots_done=sum(1 for s in required if s.state is SlotState.CONFIRMED),
            slots_total=len(required),
            next_trigger=triggers[0] if triggers else None,
        )
        return CaseAnalysis(
            case_id=case_id,
            case_type=ct,
            as_of=as_of,
            issues=issues,
            slot_statuses=slots,
            pair_decisions=decisions,
            action_triggers=triggers,
            case_card=card,
        )

    def _decide(self, extraction: ExtractionResult, timeline: Timeline) -> list[PairDecision]:
        out = []
        ids = count(1)
        for pair in candidate_pairs(extraction, timeline):
            scores = self.nli.score(pair.a, pair.b)
            if scores is None:
                continue
            model_name = self.nli.model_for(pair.a, pair.b) if isinstance(self.nli, CombinedNli) else self.nli.name
            out.append(self.policy.decide(f"pair{next(ids)}", pair.a, pair.b, scores, model_name, pair.subject_certain))
        return out

    @staticmethod
    def _stall(timeline: Timeline, requirements: CaseRequirements, as_of: date):
        if timeline.current_stage is None or requirements.stall_days is None:
            return None
        if timeline.current_stage is requirements.stages[-1] and not requirements.stall_after_final_stage:
            return None
        evs = [e for e in timeline.events if e.stage is timeline.current_stage and e.time is not None]
        records = [e for e in evs if e.evidence_level is EvidenceLevel.RECORD]
        evs = records or evs  # 기관 기록이 있으면 그 시점부터 센다
        if not evs:
            return None
        last = max(evs, key=lambda e: e.time.end)  # type: ignore[union-attr]
        since = last.time.start  # type: ignore[union-attr]
        days = (as_of - since.date()).days
        if days < requirements.stall_days:
            return None
        return timeline.current_stage, last, since, days


def _span_label(hours: float) -> str:
    if hours >= 24 * 365:
        return f"{hours / (24 * 365):.1f}년"
    if hours >= 24 * 60:
        return f"{hours / (24 * 30):.0f}개월"
    if hours >= 48:
        return f"{hours / 24:.0f}일"
    return f"{hours:.0f}시간"


def _unrecorded_facts(timeline: Timeline) -> list[tuple[TimelineEvent, TimelineEvent | None]]:
    """첫 발생 기록 이후의 발생 단계 사실 중 기록 자료로 뒷받침되지 않는 것 (목격·제보 등)."""
    occurrences = [e for e in timeline.events if e.stage is Stage.OCCURRENCE and e.time is not None]
    if not occurrences:
        return []
    first = min(occurrences, key=lambda e: e.time.start)  # type: ignore[union-attr]
    decisions = [e for e in timeline.events
                 if e.stage is Stage.OUTCOME and e.evidence_level is EvidenceLevel.RECORD and e.time is not None]
    decision = max(decisions, key=lambda e: e.time.start) if decisions else None  # type: ignore[union-attr]
    return [
        (e, decision) for e in occurrences
        if e.evidence_level is not EvidenceLevel.RECORD and e.time.start >= first.time.end  # type: ignore[union-attr,operator]
    ]


def _group_by_slot(decisions: list[PairDecision]) -> dict[ClaimSlot | None, list[PairDecision]]:
    groups: dict[ClaimSlot | None, list[PairDecision]] = {}
    for d in decisions:
        groups.setdefault(d.slot, []).append(d)
    return groups


def _claims_of(decisions: list[PairDecision], claims: dict[str, Claim]) -> list[Claim]:
    seen: dict[str, Claim] = {}
    for d in decisions:
        for cid in (d.claim_a_id, d.claim_b_id):
            seen.setdefault(cid, claims[cid])
    return list(seen.values())


def _distinct_values(claims: list[Claim]) -> list[Claim]:
    out: dict[str, Claim] = {}
    for c in sorted(claims, key=lambda c: -c.content.confidence):
        out.setdefault(display_value(c), c)
    return list(out.values())
