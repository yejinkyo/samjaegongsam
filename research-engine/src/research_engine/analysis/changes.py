"""시간이 지나며 바뀌는 값 다루기 (예: 담당 수사관 교체).

"담당자 바뀌었다고 함" 같은 변경 주장이 있으면, 그보다 앞선 기록의 값은 틀린 게 아니라 **낡았을 수 있다**.
그래서 변경 전후의 값끼리는 모순으로 비교하지 않고, 변경 이후 값이 없으면 '현재 값 확인 필요'로 올린다.
"""

from __future__ import annotations

import re
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


# ── 기록이 차례로 새로 적는 값 ─────────────────────────────────────────────
#
# 장기 사건은 같은 항목이 기록마다 차례로 바뀐다. 결정이 여러 번 내려지고(수사중지 → 재수사 → 다시
# 수사중지), 재입건되면 사건번호가 새로 붙고, 담당 수사관도 바뀐다. **서로 다른 때 나온 기록(통지서)끼리
# 값이 다른 것은 모순이 아니라 차례다.** 지금 상태는 가장 최근 기록이 말한다 — 옛 기록이 대표값이 되면
# 행동 강령 엔진이 이미 지나간 단계를 기준으로 다음 행동을 고른다.
DECISION_SLOTS = {ClaimSlot.DECISION_TYPE, ClaimSlot.DECISION_TIME}
SUCCESSIVE_SLOTS = DECISION_SLOTS | {ClaimSlot.CASE_NUMBER, ClaimSlot.INVESTIGATOR}


def record_moments(claims: list[Claim], document_dates: dict[str, Sourced[TimeValue]]) -> dict[str, datetime]:
    """이런 값을 적은 기록 자료(통지서)마다 그 기록이 나온 시점. 결정일자 → 문서 작성일 순.

    기록 자료만 센다. 진정서·진술서가 결정·사건번호·담당자를 말한 것은 새 기록이 아니라
    기록에 대한 말이라서, 기록과 다르면 여전히 어긋난 것으로 본다.
    """
    out: dict[str, datetime] = {}
    records = [c for c in claims if c.slot in SUCCESSIVE_SLOTS and c.evidence_level is EvidenceLevel.RECORD]
    for c in records:
        if c.slot is ClaimSlot.DECISION_TIME and c.slot_time is not None and c.slot_time.is_resolved:
            out[c.doc_id] = max(out.get(c.doc_id, c.slot_time.start), c.slot_time.start)
    for c in records:
        dated = document_dates.get(c.doc_id)
        if c.doc_id not in out and dated is not None and dated.value.is_resolved:
            out[c.doc_id] = dated.value.start
    return out


def latest_records(claims: list[Claim], moments: dict[str, datetime]) -> set[str] | None:
    """한 항목의 주장들 가운데 가장 최근 기록을 낸 문서(들). 기록 시점이 하나뿐이면 가를 것이 없어 None.

    항목마다 따로 가린다 — 가장 최근 통지서에 사건번호만 있고 결정은 없을 수 있다.
    """
    docs = {c.doc_id for c in claims if c.doc_id in moments}
    times = {moments[d] for d in docs}
    if len(times) < 2:
        return None
    last = max(times)
    return {d for d in docs if moments[d] == last}


def successive_records(a: Claim, b: Claim, moments: dict[str, datetime]) -> bool:
    """두 주장이 서로 다른 때 나온 기록에서 왔는가 — 그러면 모순으로 비교하지 않는다.

    같은 때 나온 기록 두 장(사본 등)은 계속 비교한다. 값이 다르면 그건 차례가 아니라 어긋남이다.
    """
    ma, mb = moments.get(a.doc_id), moments.get(b.doc_id)
    return a.slot in SUCCESSIVE_SLOTS and ma is not None and mb is not None and ma != mb


def _same_value(a: Claim, b: Claim) -> bool:
    if a.slot_time is not None and b.slot_time is not None and a.slot_time.is_resolved and b.slot_time.is_resolved:
        return a.slot_time.compatible(b.slot_time) is True
    return a.polarity == b.polarity and re.sub(r"\s+", "", a.slot_value or "") == re.sub(r"\s+", "", b.slot_value or "")


def said_of_another_record(said: Claim, record: Claim, records: list[Claim]) -> bool:
    """기록이 아닌 말(진정서·진술서)이 차례로 나온 기록 가운데 **다른 하나**와 같은 값을 말하는가.

    진정서가 지금 사건번호(2019형제20447)를 적었으면 재입건 전 통지서의 옛 번호(2007형제1182)와는
    어긋난 게 아니다 — 그 말은 다른 기록을 가리킨다. 어느 기록과도 맞지 않는 말은 계속 비교한다.
    """
    if _same_value(said, record):
        return False
    return any(r.doc_id != record.doc_id and _same_value(said, r) for r in records)

