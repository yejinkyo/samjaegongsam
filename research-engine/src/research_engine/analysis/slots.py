"""사건 유형별 추적 항목(슬롯)의 채움 상태 평가."""

from __future__ import annotations

from ..requirements import CaseRequirements
from ..schema import (
    Claim,
    ClaimSlot,
    EvidenceLevel,
    NliLabel,
    PairDecision,
    ProcessedDocument,
    SlotState,
    SlotStatus,
    SourceRef,
    Timeline,
)

S = ClaimSlot
# 읽히지 않은 영역의 OCR 추정 문자열에 이 단어가 보이면 '읽히지 않아 비어 있을 수 있음'으로 안내한다
UNREADABLE_HINTS: dict[ClaimSlot, tuple[str, ...]] = {
    S.ACCOUNT_HOLDER: ("예금주", "받는분", "받는 분", "명의", "수취인"),
    S.ACCOUNT_NUMBER: ("계좌",),
    S.TRANSFER_AMOUNT: ("금액", "원"),
    S.TRANSFER_TIME: ("일시",),
    S.RECEIPT_NUMBER: ("접수번호", "접수 번호"),
    S.RECEIPT_TIME: ("접수일",),
    S.CASE_NUMBER: ("사건번호", "사건 번호"),
    S.INVESTIGATOR: ("담당", "수사관"),
    S.TRACKING_NUMBER: ("송장",),
    S.LAST_SEEN_TIME: ("목격",),
    S.DECISION_TIME: ("결정", "처분"),
    S.DECISION_TYPE: ("결정", "처분"),
}


def display_value(claim: Claim) -> str:
    if claim.slot is S.TRANSFER_AMOUNT and claim.slot_value and claim.slot_value.isdigit():
        text = f"{int(claim.slot_value):,}원"
    elif claim.slot_time is not None:
        text = claim.slot_time.iso() or claim.slot_time.raw
    elif claim.slot in (S.SHIPMENT_SENT, S.ITEM_RECEIVED):
        text = {S.SHIPMENT_SENT: "발송함", S.ITEM_RECEIVED: "받음"}[claim.slot]
    else:
        text = claim.slot_value or claim.content.value
    if claim.polarity.value == "deny":
        text = f"아님({text})" if claim.slot not in (S.SHIPMENT_SENT, S.ITEM_RECEIVED) else {
            S.SHIPMENT_SENT: "발송하지 않음", S.ITEM_RECEIVED: "받지 못함"}[claim.slot]
    return text


def evaluate_slots(
    requirements: CaseRequirements,
    claims: list[Claim],
    decisions: list[PairDecision],
    docs: list[ProcessedDocument],
    timeline: Timeline,
    min_confidence: float = 0.7,
) -> list[SlotStatus]:
    flow = requirements.stages
    current_idx = flow.index(timeline.current_stage) if timeline.current_stage in flow else -1
    contradicted = {cid for d in decisions if d.label is NliLabel.CONTRADICTION for cid in (d.claim_a_id, d.claim_b_id)}
    out: list[SlotStatus] = []
    for req in requirements.slots:
        stage_idx = flow.index(req.stage) if req.stage in flow else 0
        if stage_idx > current_idx + 1:
            continue  # 아직 도달하지 않은 단계의 항목은 '빠짐'으로 보지 않는다
        cs = [c for c in claims if c.slot is req.slot and (req.subject is None or c.subject in (req.subject, None))]
        confident = [c for c in cs if c.content.confidence >= min_confidence]
        records = [c for c in confident if c.evidence_level is EvidenceLevel.RECORD]
        state: SlotState
        chosen: list[Claim]
        region_refs: list[SourceRef] = []
        if any(c.claim_id in contradicted for c in cs):
            state, chosen = SlotState.CONFLICTING, [c for c in cs if c.claim_id in contradicted]
        elif records:
            state, chosen = SlotState.CONFIRMED, records
        elif confident:
            state, chosen = SlotState.CLAIMED_ONLY, confident
        elif cs:
            state, chosen = SlotState.LOW_CONFIDENCE, cs
        else:
            hints = UNREADABLE_HINTS.get(req.slot, ())
            regions = [u for d in docs for u in d.unreadable if any(h in u.ocr_guess for h in hints)]
            state, chosen = (SlotState.UNREADABLE if regions else SlotState.MISSING), []
            region_refs = [
                SourceRef(source_doc_id=u.doc_id, page=u.page, source_line=u.line_no, source_bbox=u.bbox)
                for u in regions
            ]
        out.append(
            SlotStatus(
                slot=req.slot,
                label=req.label,
                stage=req.stage,
                required=req.required,
                state=state,
                value=display_value(chosen[0]) if chosen and state is SlotState.CONFIRMED else None,
                claim_ids=[c.claim_id for c in chosen],
                sources=[c.content.ref() for c in chosen] + region_refs,
            )
        )
    return out
