"""시간이 지나며 바뀌는 값 다루기 (예: 담당 수사관 교체).

"담당자 바뀌었다고 함" 같은 변경 주장이 있으면, 그보다 앞선 기록의 값은 틀린 게 아니라 **낡았을 수 있다**.
그래서 변경 전후의 값끼리는 모순으로 비교하지 않고, 변경 이후 값이 없으면 '현재 값 확인 필요'로 올린다.
"""

from __future__ import annotations

from datetime import datetime

from ..schema import Claim, ClaimSlot, EvidenceLevel, Sourced, TimeValue

# 변경 주장 슬롯 → 바뀌는 값 슬롯
CHANGE_OF: dict[ClaimSlot, ClaimSlot] = {ClaimSlot.INVESTIGATOR_CHANGE: ClaimSlot.INVESTIGATOR}
CHANGE_FOR: dict[ClaimSlot, ClaimSlot] = {v: k for k, v in CHANGE_OF.items()}


def claim_time(claim: Claim, document_dates: dict[str, Sourced[TimeValue]]) -> datetime | None:
    """주장이 가리키는 시점: 슬롯 시각 → 메시지 시각 → 문서 작성일 순."""
    for tv in (claim.slot_time, claim.said_at, document_dates[claim.doc_id].value if claim.doc_id in document_dates else None):
        if tv is not None and tv.is_resolved:
            return tv.start
    return None


def latest_change(claims: list[Claim], value_slot: ClaimSlot, document_dates: dict[str, Sourced[TimeValue]]) -> Claim | None:
    change_slot = CHANGE_FOR.get(value_slot)
    changes = [c for c in claims if change_slot is not None and c.slot is change_slot]
    if not changes:
        return None
    # 시점을 모르는 변경은 가장 최근으로 본다 (낡았을 가능성을 놓치지 않도록)
    return max(changes, key=lambda c: (claim_time(c, document_dates) is None, claim_time(c, document_dates) or datetime.min))


def is_after_change(claim: Claim, change: Claim, document_dates: dict[str, Sourced[TimeValue]]) -> bool:
    """값 주장이 변경 이후의 것인가. 알 수 없으면 False(변경 이전 = 낡았을 수 있음)로 본다."""
    same_doc = claim.doc_id == change.doc_id and claim.content.source_line and change.content.source_line
    if same_doc and claim.content.source_line >= change.content.source_line:  # type: ignore[operator]
        return True  # 같은 메모에서 "담당자 바뀜" 다음 줄에 적힌 이름
    t_claim, t_change = claim_time(claim, document_dates), claim_time(change, document_dates)
    return t_claim is not None and t_change is not None and t_claim >= t_change


# ── 여러 번 내려지는 결정 ─────────────────────────────────────────────────
#
# 한 사건에 결정이 여러 번 내려질 수 있다(수사중지 → 재수사 → 다시 수사중지). 통지서마다 결정
# 내용·일자가 다른 것은 모순이 아니라 차례다. 지금 사건의 상태는 **가장 최근 결정**이 말한다 —
# 옛 결정이 대표값이 되면 행동 강령 엔진이 이미 지나간 단계를 기준으로 다음 행동을 고른다.
DECISION_SLOTS = {ClaimSlot.DECISION_TYPE, ClaimSlot.DECISION_TIME}


def decision_moments(claims: list[Claim], document_dates: dict[str, Sourced[TimeValue]]) -> dict[str, datetime]:
    """결정을 알린 기록 자료(통지서)마다 그 결정의 시점. 결정일자 → 문서 작성일 순.

    기록 자료만 센다. 진정서·진술서가 결정을 언급한 것은 새 결정이 아니라 결정에 대한 말이다.
    """
    out: dict[str, datetime] = {}
    records = [c for c in claims if c.slot in DECISION_SLOTS and c.evidence_level is EvidenceLevel.RECORD]
    for c in records:
        if c.slot is ClaimSlot.DECISION_TIME and c.slot_time is not None and c.slot_time.is_resolved:
            out[c.doc_id] = max(out.get(c.doc_id, c.slot_time.start), c.slot_time.start)
    for c in records:
        dated = document_dates.get(c.doc_id)
        if c.doc_id not in out and dated is not None and dated.value.is_resolved:
            out[c.doc_id] = dated.value.start
    return out


def latest_decision_doc(moments: dict[str, datetime]) -> str | None:
    """가장 최근 결정을 알린 문서. 결정이 하나뿐(시점이 하나)이면 가를 것이 없어 None."""
    if len(set(moments.values())) < 2:
        return None
    return max(moments, key=lambda doc_id: moments[doc_id])


def separate_decisions(a: Claim, b: Claim, moments: dict[str, datetime]) -> bool:
    """두 주장이 서로 다른 결정을 알린 통지서에서 왔는가 — 그러면 모순으로 비교하지 않는다."""
    ma, mb = moments.get(a.doc_id), moments.get(b.doc_id)
    return a.slot in DECISION_SLOTS and ma is not None and mb is not None and ma != mb

