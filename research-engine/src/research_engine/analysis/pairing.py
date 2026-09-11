"""NLI에 넣을 Claim 쌍 고르기: 서로 다른 문서, 같은 슬롯, 같은(또는 같을 수 있는) 대상."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ..schema import Claim, ClaimSlot, ExtractionResult, Timeline
from ..timeline.coref import mask_compatible

S = ClaimSlot
# 한 사건 안에 여러 번 일어날 수 있어 슬롯만으로는 같은 일인지 알 수 없는 항목 — 쌍으로 비교하지 않는다
UNPAIRED_SLOTS = {S.INCIDENT_TIME}


@dataclass
class ClaimPair:
    a: Claim
    b: Claim
    subject_certain: bool


def _relation(a: Claim, b: Claim, transfer_times: dict[str, list[Claim]]) -> str:
    """'same' | 'different' | 'unknown'."""
    slot = a.slot
    if slot is S.ACCOUNT_NUMBER:
        if a.subject and b.subject:
            return "same" if a.subject == b.subject else "different"
        return "unknown"
    if slot is S.ACCOUNT_HOLDER:
        if a.subject and b.subject:
            same = a.subject == b.subject or mask_compatible(a.subject, b.subject)[0]
            return "same" if same else "different"
        return "unknown"
    if slot is S.TRANSFER_TIME:
        if a.subject and b.subject:
            return "same" if a.subject == b.subject else "unknown"  # 금액이 다르면 같은 송금인지 모름
        return "unknown"
    if slot is S.TRANSFER_AMOUNT:
        ta, tb = transfer_times.get(a.doc_id, []), transfer_times.get(b.doc_id, [])
        if len(ta) == 1 and len(tb) == 1 and ta[0].slot_time and tb[0].slot_time:
            compatible = ta[0].slot_time.compatible(tb[0].slot_time)
            if compatible and not (ta[0].slot_time.approximate and tb[0].slot_time.approximate):
                return "same"
            return "different" if compatible is False else "unknown"
        return "unknown"
    if slot is S.DECISION_TIME:
        # 한 사건에 결정이 여러 번(불송치 → 재수사 → 수사중지) 있을 수 있다: 같은 종류의 결정일 때만 확실
        return "same" if a.subject and a.subject == b.subject else "unknown"
    if slot in (S.RECEIPT_TIME, S.DECISION_TYPE):
        return "unknown"
    return "same"


def candidate_pairs(extraction: ExtractionResult, timeline: Timeline | None = None) -> list[ClaimPair]:
    claims = [c for c in extraction.claims if c.slot is not None and c.slot not in UNPAIRED_SLOTS]
    transfer_times: dict[str, list[Claim]] = {}
    for c in claims:
        if c.slot is S.TRANSFER_TIME and c.slot_time is not None and c.slot_time.is_resolved:
            transfer_times.setdefault(c.doc_id, []).append(c)

    pairs: list[ClaimPair] = []
    by_slot: dict[ClaimSlot, list[Claim]] = {}
    for c in claims:
        by_slot.setdefault(c.slot, []).append(c)  # type: ignore[arg-type]
    for group in by_slot.values():
        for a, b in combinations(group, 2):
            if a.doc_id == b.doc_id:
                continue
            relation = _relation(a, b, transfer_times)
            if relation == "different":
                continue
            pairs.append(ClaimPair(a, b, relation == "same"))
    pairs.extend(_text_pairs(extraction, timeline))
    return pairs


def _text_pairs(extraction: ExtractionResult, timeline: Timeline | None) -> list[ClaimPair]:
    """슬롯 없는 주장끼리: 다른 문서·다른 화자이면서 같은 엔티티를 언급한 경우만 (텍스트 NLI용)."""
    if timeline is None:
        return []
    entities_by_line: dict[tuple[str, int], set[str]] = {}
    for m in extraction.mentions:
        ent = timeline.mention_to_entity.get(m.mention_id)
        if ent and m.name.source_line is not None:
            entities_by_line.setdefault((m.doc_id, m.name.source_line), set()).add(ent)
    free = [c for c in extraction.claims if c.slot is None and c.content.source_line is not None]
    pairs = []
    for a, b in combinations(free, 2):
        if a.doc_id == b.doc_id or a.speaker == b.speaker:
            continue
        ea = entities_by_line.get((a.doc_id, a.content.source_line), set())  # type: ignore[arg-type]
        eb = entities_by_line.get((b.doc_id, b.content.source_line), set())  # type: ignore[arg-type]
        if ea & eb:
            pairs.append(ClaimPair(a, b, subject_certain=False))
    return pairs
