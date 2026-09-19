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
    Sourced,
    SourceRef,
    Timeline,
    TimeValue,
)
from .changes import DECISION_SLOTS, decision_moments, is_after_change, latest_change, latest_decision_doc

S = ClaimSlot
TIME_SLOTS = {S.TRANSFER_TIME, S.RECEIPT_TIME, S.INCIDENT_TIME, S.LAST_SEEN_TIME, S.LAST_CONTACT_TIME, S.DECISION_TIME}
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
    elif claim.slot in TIME_SLOTS and claim.slot_time is not None:
        text = claim.slot_time.iso() or claim.slot_time.raw
    elif claim.slot in (S.SHIPMENT_SENT, S.ITEM_RECEIVED):
        text = {S.SHIPMENT_SENT: "발송함", S.ITEM_RECEIVED: "받음"}[claim.slot]
    else:
        text = claim.slot_value or claim.content.value
    if claim.polarity.value == "deny":
        text = f"아님({text})" if claim.slot not in (S.SHIPMENT_SENT, S.ITEM_RECEIVED) else {
            S.SHIPMENT_SENT: "발송하지 않음", S.ITEM_RECEIVED: "받지 못함"}[claim.slot]
    return text


def most_specific_first(claims: list[Claim]) -> list[Claim]:
    """같은 사실을 덜 구체적으로 적은 자료가 섞이면 더 구체적인 쪽을 대표로 세운다.

    통지서는 제목과 결정내용란에 같은 결정을 다르게 적는다.

        1줄  수사중지 결정 통지서          → '수사중지'
        6줄  결정내용 수사중지(참고인중지)  → '수사중지(참고인중지)'

    둘 다 기록이라 앞줄이 대표가 되면 중지 사유가 사라지고, 행동 강령 엔진은
    피의자중지·참고인중지를 가르지 못해 되묻게 된다. 한 값이 다른 값을 그대로
    품고 있을 때만 순서를 바꾼다 — 서로 다른 값이면 모순 판정의 몫이다.
    """
    if len(claims) < 2:
        return claims
    values = [display_value(c) for c in claims]

    def covers(i: int) -> int:
        return sum(1 for j, v in enumerate(values) if v != values[i] and v in values[i])

    best = max(range(len(claims)), key=lambda i: (covers(i), len(values[i])))
    if covers(best) == 0:
        return claims
    return [claims[best]] + [c for i, c in enumerate(claims) if i != best]


def evaluate_slots(
    requirements: CaseRequirements,
    claims: list[Claim],
    decisions: list[PairDecision],
    docs: list[ProcessedDocument],
    timeline: Timeline,
    min_confidence: float = 0.7,
    document_dates: dict[str, Sourced[TimeValue]] | None = None,
) -> list[SlotStatus]:
    dd = document_dates or {}
    flow = requirements.stages
    current_idx = flow.index(timeline.current_stage) if timeline.current_stage in flow else -1
    contradicted = {cid for d in decisions if d.label is NliLabel.CONTRADICTION for cid in (d.claim_a_id, d.claim_b_id)}
    out: list[SlotStatus] = []
    for req in requirements.slots:
        stage_idx = flow.index(req.stage) if req.stage in flow else 0
        if stage_idx > current_idx + 1:
            continue  # 아직 도달하지 않은 단계의 항목은 '빠짐'으로 보지 않는다
        cs = [c for c in claims if c.slot is req.slot and (req.subject is None or c.subject in (req.subject, None))]
        if req.slot in DECISION_SLOTS:
            # 결정이 여러 번이면 가장 최근 통지서의 값이 지금 상태다. 옛 통지서는 이력이지 낡은 값이 아니다.
            moments = decision_moments(claims, dd)
            latest = latest_decision_doc(moments)
            if latest is not None:
                cs = [c for c in cs if c.doc_id == latest or c.doc_id not in moments]
        change = latest_change(claims, req.slot, dd)
        stale: list[Claim] = []
        if change is not None:
            stale = [c for c in cs if not is_after_change(c, change, dd)]
            cs = [c for c in cs if is_after_change(c, change, dd)]
        confident = [c for c in cs if c.content.confidence >= min_confidence]
        records = [c for c in confident if c.evidence_level is EvidenceLevel.RECORD]
        state: SlotState
        chosen: list[Claim]
        region_refs: list[SourceRef] = []
        if any(c.claim_id in contradicted for c in cs):
            state, chosen = SlotState.CONFLICTING, [c for c in cs if c.claim_id in contradicted]
        elif records:
            state, chosen = SlotState.CONFIRMED, most_specific_first(records)
        elif confident:
            state, chosen = SlotState.CLAIMED_ONLY, confident
        elif cs:
            state, chosen = SlotState.LOW_CONFIDENCE, cs
        else:
            hints = UNREADABLE_HINTS.get(req.slot, ())
            regions = [u for d in docs for u in d.unreadable if any(h in u.ocr_guess for h in hints)]
            region_refs = [
                SourceRef(source_doc_id=u.doc_id, page=u.page, source_line=u.line_no, source_bbox=u.bbox)
                for u in regions
            ]
            if stale:
                # 예전 값은 있지만 바뀌었다는 내용이 있고, 바뀐 값은 없음 (마지막 항목 = 변경 주장)
                old = sorted(stale, key=lambda c: (c.evidence_level is not EvidenceLevel.RECORD, -c.content.confidence))
                state, chosen = SlotState.OUTDATED, old + [change]  # type: ignore[list-item]
            else:
                state, chosen = (SlotState.UNREADABLE if regions else SlotState.MISSING), []
        out.append(
            SlotStatus(
                slot=req.slot,
                label=req.label,
                stage=req.stage,
                required=req.required,
                state=state,
                value=display_value(chosen[0]) if chosen and state in (SlotState.CONFIRMED, SlotState.OUTDATED) else None,
                claim_ids=[c.claim_id for c in chosen],
                sources=[c.content.ref() for c in chosen] + region_refs,
            )
        )
    return out
