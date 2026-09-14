"""5단계 — 필요 서류 ↔ 자료함 대조.

집합 연산이라 LLM 이 필요 없다. 사전이 알려준 필요 서류 목록과 사용자가 실제로 가진
자료를 맞춰 보면 끝이다. 그래서 기능이 늘어도 설명 가능성이 줄지 않는다.

장기·미제 사건에서는 **"없다"와 "더는 구할 수 없다"가 다른 정보**다.
보존 기한이 지난 자료는 구해 오라고 안내하면 안 되고 다른 경로를 알려줘야 한다.
그래서 상태를 넷으로 나눈다.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .schema import CheckItem, Checklist, Deadline

DATA = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def load_documents() -> dict[str, Any]:
    return json.loads((DATA / "documents.json").read_text(encoding="utf-8"))


def build_checklist(
    action: str | None,
    documents: list[dict[str, Any]],
    deadlines: list[Deadline] | None = None,
    st: str | None = None,
) -> Checklist:
    """액션 하나에 필요한 서류를 자료함과 맞춰 본다.

    같은 액션이라도 절차 단계에 따라 서류가 다르다 — '불복'은 불송치면 이의신청서,
    불기소면 항고장, 수사중지면 이의제기서다. 사전에 ``by_stage`` 가 있으면 ST 로 한 번 더
    갈라 조회한다.

    사전에 항목이 없으면 빈 체크리스트를 돌려준다 — 화면은 아무것도 그리지 않는다.
    기한과 같은 원칙이다. 없는 것을 지어내면 빠진 서류 때문에 신청이 반려된다.
    """
    kb = load_documents()
    actions = kb.get("actions") or {}
    entry = actions.get(action or "") or {}

    # 단계별로 서류가 갈리는 액션은 ST 로 다시 조회한다
    by_stage = entry.get("by_stage") or {}
    if by_stage and st:
        resolved = by_stage.get(st)
        if resolved:
            action = resolved
            entry = actions.get(resolved) or {}

    # 자료를 확보하는 단계는 제출 서류가 원래 없다. '못 채움'으로 띄우면 안 된다
    if entry.get("no_submission"):
        return Checklist(action=action, no_submission=entry.get("why"), advisory=entry.get("advisory"))

    rows = entry.get("items") or []

    if not rows:
        return Checklist(
            action=action,
            unresolved="필요 서류가 지식베이스에 아직 없습니다 — 법령·서식 확인 필요",
        )

    # 보존 기한이 지난 자료 종류는 '확보불가'로 내린다
    expired_kinds: set[str] = set()
    for d in deadlines or []:
        if d.code == "TIM-031" and d.severity == "expired":
            expired_kinds |= {"messenger", "digital"}

    have_kinds = {d.get("doc_type") for d in documents}
    by_kind: dict[str, list[str]] = {}
    for d in documents:
        by_kind.setdefault(d.get("doc_type"), []).append(d.get("doc_id"))

    items: list[CheckItem] = []
    for row in rows:
        kinds = set(row.get("대응_자료종류") or [])
        matched = sorted({doc for k in kinds & have_kinds for doc in by_kind[k]})

        if matched:
            state, reason = "보유", None
        elif kinds & expired_kinds:
            state, reason = "확보불가", "보존 기한이 지났습니다"
        elif row.get("생성가능"):
            state, reason = "생성가능", None
        else:
            state, reason = "미보유", None

        items.append(CheckItem(
            label=row["항목"],
            required=bool(row.get("필수")),
            state=state,
            reason=reason,
            doc_ids=matched,
        ))

    done = sum(1 for i in items if i.state == "보유")
    return Checklist(
        action=action, items=items, done=done, total=len(items),
        form_name=entry.get("form_name"),
        form_url=entry.get("form_url"),
        submit_to=entry.get("submit_to"),
        statute=entry.get("statute"),
        prerequisite=entry.get("prerequisite"),
        source=entry.get("source"),
        advisory=entry.get("advisory"),
    )
