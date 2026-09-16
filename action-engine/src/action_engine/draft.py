"""낼 서류의 초안을 조립한다 — 규칙만으로.

화면은 지금까지 "이 서류가 필요합니다"까지만 말하고 서류를 만들어 주지는 못했다.
그 마지막 조각이다. 여기에는 모델이 없다. **모델 없이도 나오는 골격**이 먼저다 —
발표 중에 API 가 죽어도 화면이 빈칸이 되면 안 된다. 문장을 다듬는 층은 이 위에 얹는다.

넘지 않는 선이 이 모듈의 본체다.

1. **사실은 전부 타임라인에서 온다.** 없는 사실을 채우지 않는다.
2. **출처 없는 줄은 버린다.** 몇 줄을 버렸는지는 ``dropped`` 에 남긴다.
3. **법조문·제출처·서식명은 지식베이스에서만 온다.** 없으면 빈칸과 이유를 남긴다.
4. **진술과 기록을 섞지 않는다.** 어느 쪽에서 왔는지를 줄마다 들고 간다.
5. **평가하지 않는다.** '부당합니다' 같은 말을 만들지 않는다. 그래서 문장을 새로 짓지 않고
   자료의 날짜와 문구를 그대로 옮긴다. 이의 사유처럼 판단이 들어가야 하는 칸은
   **비워 두고 직접 쓰라고 적는다.**
6. **초안 표시를 떼지 않는다** (``is_draft``).
"""

from __future__ import annotations

from typing import Any

from .schema import CaseCardOut, Citation, DraftDocument, DraftField, DraftLine, DraftSection

# 서식 머리에 들어가는 칸 ← 사건 기록에서 찾아 채운다. 없으면 빈칸으로 남는다.
FIELDS_FROM_RECORD: list[tuple[str, str]] = [
    ("case_number", "사건번호"),
    ("receipt_number", "접수번호"),
    ("investigator", "담당 수사관"),
    ("decision_type", "결정 내용"),
    ("decision_time", "결정일"),
]

# 자료에 있을 수 없는 칸. 물어보지 않고 지어내면 그대로 남의 이름이 적힌다.
FIELDS_FROM_USER: list[tuple[str, str]] = [
    ("applicant_name", "신청인 성명"),
    ("applicant_contact", "신청인 연락처"),
    ("applicant_address", "신청인 주소"),
]

_MONTHS = "{y}. {m}. {d}."


def _date_text(time: dict[str, Any] | None) -> str | None:
    """이벤트 시각을 서류에 적는 모양으로. 날짜를 모르면 만들지 않는다."""
    if not time:
        return None
    start = time.get("start")
    if not start:
        return None
    y, m, d = start[:10].split("-")
    gran = time.get("granularity")
    if gran == "year":
        return f"{int(y)}년"
    if gran == "month":
        return f"{int(y)}. {int(m)}."
    return _MONTHS.format(y=int(y), m=int(m), d=int(d))


def _citations(event: dict[str, Any], docs: dict[str, dict]) -> list[Citation]:
    """출처를 줄 단위로. 같은 줄이 여러 번 걸리면 한 번만 남긴다."""
    seen: set[tuple[str, int | None, int | None]] = set()
    out: list[Citation] = []
    for src in event.get("sources") or []:
        doc_id = src.get("source_doc_id")
        if not doc_id:
            continue
        key = (doc_id, src.get("page"), src.get("source_line"))
        if key in seen:
            continue
        seen.add(key)
        out.append(Citation(
            doc_id=doc_id,
            file_name=(docs.get(doc_id) or {}).get("file_name"),
            page=src.get("page"),
            line=src.get("source_line"),
            quote=src.get("quote"),
        ))
    return out


def _history(result: dict[str, Any], docs: dict[str, dict]) -> tuple[list[DraftLine], int]:
    """사건 경위 — 시간순 골격. 출처가 없는 사건은 넣지 않는다."""
    lines: list[DraftLine] = []
    dropped = 0

    events = list(result.get("timeline", {}).get("events") or [])
    events.sort(key=lambda e: ((e.get("time") or {}).get("start") or "9999"))

    for event in events:
        cites = _citations(event, docs)
        if not cites:
            # 출처를 달 수 없는 문장은 초안에서 버린다 (Sourced 원칙과 같다)
            dropped += 1
            continue
        title = (event.get("title") or "").strip()
        if not title:
            dropped += 1
            continue
        lines.append(DraftLine(
            date=_date_text(event.get("time")),
            text=title,
            evidence_level=event.get("evidence_level") or "record",
            citations=cites,
        ))
    return lines, dropped


def _slot_values(result: dict[str, Any]) -> dict[str, tuple[str | None, str]]:
    """슬롯 값과 그 상태. '기록으로 확인'과 '말만 있음'을 구별해서 들고 간다."""
    out: dict[str, tuple[str | None, str]] = {}
    for status in result.get("analysis", {}).get("slot_statuses") or []:
        slot = status.get("slot")
        if slot:
            out[slot] = (status.get("value"), status.get("state") or "")
    return out


def build_draft(result: dict[str, Any], card: CaseCardOut, action: str | None = None) -> DraftDocument | None:
    """낼 서류 하나의 초안. 만들 서류가 정해져 있지 않으면 None.

    ``action`` 을 주지 않으면 지금의 다음 행동으로 만든다.
    """
    from .checklist import build_checklist

    action = action or (card.next_action.action if card.next_action else None)
    if not action:
        return None

    check = build_checklist(action, result.get("documents", []), card.tim, st=card.st.code)
    if not check.form_name:
        # 낼 서류가 사전에 없다. 서식 이름을 지어내면 그대로 잘못된 서류를 쓰게 된다.
        return None

    docs = {d["doc_id"]: d for d in result.get("documents", [])}
    slots = _slot_values(result)

    fields: list[DraftField] = []
    unfilled: list[DraftField] = []

    for key, labelname in FIELDS_FROM_RECORD:
        value, state = slots.get(key, (None, ""))
        if value and state == "confirmed":
            fields.append(DraftField(key=key, label=labelname, value=str(value), filled_from="case_record"))
        elif value:
            # 값은 있지만 기록으로 확인되지 않았다. 서식에 그대로 옮기면 안 된다.
            unfilled.append(DraftField(
                key=key, label=labelname,
                reason=f"자료에 '{value}' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요.",
            ))
        else:
            unfilled.append(DraftField(key=key, label=labelname, reason="자료에서 찾지 못했습니다."))

    for key, labelname in FIELDS_FROM_USER:
        unfilled.append(DraftField(key=key, label=labelname, reason="자료에 있을 수 없는 항목입니다. 직접 적어 주세요."))

    # 제출처·근거 법령은 지식베이스 값을 그대로 옮긴다
    for key, labelname, value in (
        ("form_name", "서식", check.form_name),
        ("submit_to", "제출처", check.submit_to),
        ("statute", "근거 법령", check.statute),
    ):
        if value:
            fields.append(DraftField(key=key, label=labelname, value=value, filled_from="knowledge_base"))
        else:
            unfilled.append(DraftField(key=key, label=labelname, reason="지식베이스에 아직 없습니다 — 확인 필요"))

    lines, dropped = _history(result, docs)

    sections = [
        DraftSection(
            heading="사건 경위",
            lines=lines,
            note="자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
        ),
        DraftSection(
            heading="이의 사유",
            note="타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
        ),
    ]

    return DraftDocument(
        action=action,
        form_name=check.form_name,
        form_source=check.form_source,
        form_url=check.form_url,
        submit_to=check.submit_to,
        statute=check.statute,
        fields=fields,
        unfilled=unfilled,
        sections=sections,
        dropped=dropped,
    )
