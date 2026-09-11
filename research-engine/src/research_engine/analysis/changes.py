"""시간이 지나며 바뀌는 값 다루기 (예: 담당 수사관 교체).

"담당자 바뀌었다고 함" 같은 변경 주장이 있으면, 그보다 앞선 기록의 값은 틀린 게 아니라 **낡았을 수 있다**.
그래서 변경 전후의 값끼리는 모순으로 비교하지 않고, 변경 이후 값이 없으면 '현재 값 확인 필요'로 올린다.
"""

from __future__ import annotations

from datetime import datetime

from ..schema import Claim, ClaimSlot, Sourced, TimeValue

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
