"""사건 유형별 추적 항목(슬롯) 정의.

어떤 항목이 '절차상 필수'인지는 도메인 지식이므로 코드가 아닌 데이터로 둔다.
``status``가 ``verified``가 되기 전까지 결과 화면은 초안임을 알려야 한다.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from ..schema import ClaimSlot, Stage


class SlotRequirement(BaseModel):
    slot: ClaimSlot
    stage: Stage
    label: str
    required: bool = True
    subject: str | None = Field(default=None, description="슬롯 안 대상 제한 (예: 입금 계좌만)")


class CaseRequirements(BaseModel):
    case_type: str
    label: str
    status: Literal["draft_unverified", "verified"]
    note: str = ""
    stages: list[Stage]
    gap_threshold_hours: float | None = None
    stall_days: int | None = None
    slots: list[SlotRequirement]

    def slot(self, slot: ClaimSlot) -> SlotRequirement | None:
        return next((s for s in self.slots if s.slot is slot), None)


def available_case_types() -> list[str]:
    return sorted(p.name[:-5] for p in resources.files(__package__).iterdir() if p.name.endswith(".json"))


def load_requirements(case_type: str, path: str | Path | None = None) -> CaseRequirements:
    if path is not None:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        resource = resources.files(__package__) / f"{case_type}.json"
        if not resource.is_file():
            raise ValueError(f"알 수 없는 사건 유형: {case_type} (가능: {', '.join(available_case_types())})")
        raw = resource.read_text(encoding="utf-8")
    return CaseRequirements.model_validate(json.loads(raw))
