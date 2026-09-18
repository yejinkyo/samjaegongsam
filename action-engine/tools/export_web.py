"""화면(web/)이 읽을 데이터를 만든다.

research-engine 출력(테스트 픽스처)을 build_card() 에 통과시키고, 화면에 필요한 값만 골라
``web/data/cases.js`` 로 쓴다. 화면은 정적 HTML 이라 서버 없이 파일을 열어도 동작해야 해서
JSON 이 아니라 전역 변수에 담는다.

화면 문장은 엔진이 만든 값에서만 온다. 절차(무엇을·어디에·어떻게·언제까지)가 지식베이스에
없으면 비워 두고 '확인 중'으로 표시한다 — 피그마 시안의 예시 문구를 채워 넣지 않는다.

    cd action-engine
    uv run python tools/export_web.py

화면에서 새로 등록한 사건은 web/serve.py 가 사건 하나씩 이 스크립트로 넘긴다.

    uv run python tools/export_web.py --result out.json --id <사건 id> --title <사건 이름> --out view.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from action_engine import build_card

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
OUT = ROOT / "web" / "data" / "cases.js"

# 화면에 올릴 예시 사건. 픽스처에는 사용자가 붙인 사건 이름이 없어 여기서 준다(인물·사건은 가상).
CASES = [
    ("used_goods_fraud", "중고거래 사기 피해"),
    ("long_unsolved_missing", "2015년 실종 사건"),
    ("suspension_recent", "고소 사건 (수사중지)"),
]

# 직접 만든 사건을 화면에서도 보려고 여기에 적는다. 파일이 없으면 위의 세 건만 올라간다.
#
#   [{"id": "missing_2006", "title": "2006년 실종 사건",
#     "result": "시험자료/장기미제-재수사/out.json"}]
#
# 목록을 명령줄이 아니라 파일로 두는 이유: cases.js 는 늘 이 스크립트의 출력과 같아야 한다
# (test_커밋된_화면_데이터가_엔진_출력과_같다). 명령줄로만 끼워 넣으면 그 약속이 깨진다.
EXTRA_CASES = ROOT / "시험자료" / "사이트에-올릴-사건.json"

# 규칙이 고른 액션 키의 화면 이름. 절차 문구가 아니라 '무엇에 관한 행동인가'만 적는다.
ACTION_LABELS = {
    "ACT-공소시효": "공소시효가 끝나기 전에 할 수 있는 절차 확인",
    "ACT-불복기한": "기한 안에 결정에 대한 불복 절차 진행",
    "ACT-증거보존": "사라지기 전에 증거 보존",
    "ACT-단계확인": "지금 사건이 어느 단계인지 확인",
    "ACT-신규정보제출": "새로 확인된 정보를 수사기관에 제출",
    "ACT-모순확인": "자료끼리 어긋난 부분 확인 요청",
    "ACT-기록열람": "수사 기록 열람 신청",
    "ACT-근거보완": "주장을 뒷받침할 근거 자료 보완",
    "ACT-공백보완": "기록이 빈 기간의 자료 확보",
    "ACT-상시": "정보공개청구 등 언제든 할 수 있는 경로",
}

ISSUE_GROUPS = [
    ("inconsistency", "자료끼리 어긋남", "conflict"),
    ("unverified", "확인되지 않음", "unknown"),
    ("missing", "빠진 정보", "gap"),
    ("unreadable", "읽히지 않은 부분", "gap"),
]

ENTITY_GROUPS = [
    ("person", "사람"),
    ("organization", "기관"),
    ("account", "계좌"),
    ("case_number", "사건번호"),
    ("receipt_number", "접수번호"),
    ("phone", "연락처"),
]

# 항목 키의 화면 이름. 엔진이 비교할 수 있게 구조화한 슬롯을 사람 말로 바꾼다.
SLOT_LABELS = {
    "incident_time": "사건 발생 시점",
    "last_seen_time": "마지막 목격 시점",
    "last_contact_time": "마지막 연락 시점",
    "transfer_amount": "송금 금액",
    "transfer_time": "송금 시점",
    "account_number": "계좌번호",
    "account_holder": "예금주",
    "shipment_sent": "발송 여부",
    "tracking_number": "송장번호",
    "report_time": "신고 시점",
    "receipt_number": "접수번호",
    "receipt_time": "접수일시",
    "case_number": "사건번호",
    "investigator": "담당 수사관",
    "decision_type": "결정 내용",
    "decision_time": "결정일",
}

# 항목 상태 — '확인됨'과 '말만 있음'을 섞지 않는다
SLOT_STATES = {
    "confirmed": ("기록으로 확인", "verified"),
    "claimed_only": ("말만 있고 기록 없음", "unverified"),
    "conflicting": ("자료마다 다름", "conflict"),
    "low_confidence": ("판독 신뢰도 낮음", "unverified"),
    "outdated": ("낡았을 수 있음", "unverified"),
    "missing": ("자료에 없음", "unverified"),
    "suspected_conflict": ("차이 의심", "conflict"),
}

CIRCLED = "".join(chr(0x2460 + i) for i in range(20))  # ①~⑳


# 사건 유형별 진행 단계 — 화면에 보이는 이름이다.
#
# 엔진의 Stage 는 여섯 가지(발생·송금·신고·접수·수사·결과)로 사건 유형을 가리지 않는다.
# 화면에서는 그 사건이 실제로 밟는 절차 이름으로 보여야 한다. 수사중지 사건에서 마지막이
# '결과'로 끝나면 사용자는 사건이 끝난 줄 안다 — 실제로는 '중지'이고 그 뒤에 되살릴 길이 남아 있다.
# 엔진 코드는 그대로 두고 여기서 묶어서 이름만 바꾼다.
STAGE_TRACKS = {
    "missing_person_suspended": [
        ("발생", ["occurrence"]),
        ("신고", ["report", "receipt"]),
        ("수사", ["investigation"]),
        ("중지", ["outcome"]),
        ("재수사", []),      # 아직 오지 않은 단계 — 이의제기·새 자료로 열린다
    ],
    "investigation_suspended": [
        ("고소", ["occurrence", "report"]),
        ("접수", ["receipt"]),
        ("수사", ["investigation"]),
        ("중지", ["outcome"]),
        ("재개", []),
    ],
}


def _stages(card) -> list[dict[str, str]]:
    engine = {s["stage"]: s["state"] for s in card.stages}
    track = STAGE_TRACKS.get(card.case_type)
    if not track:
        # 유형별 이름을 정하지 않은 사건은 엔진 단계를 그대로 쓴다
        return [{"label": s["label"], "state": {"done": "done", "current": "current"}.get(s["state"], "todo")}
                for s in card.stages]

    rows = []
    for label, codes in track:
        states = [engine[c] for c in codes if c in engine]
        if "current" in states:
            state = "current"
        elif states and all(st == "done" for st in states):
            state = "done"
        elif "done" in states:
            state = "done"
        else:
            state = "todo"   # 자료가 없거나(skipped) 아직 오지 않은 단계
        rows.append({"label": label, "state": state})
    return rows


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _kind(file_name: str, doc_type: str) -> str:
    if doc_type == "user_note":
        return "메모"
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    return {"pdf": "PDF", "png": "IMG", "jpg": "IMG", "jpeg": "IMG"}.get(ext, "파일")


def _event_time(t: dict[str, Any], multi_year: bool) -> str:
    start, end = _dt(t.get("start")), _dt(t.get("end"))
    if not start:
        return "시각 미상"
    day = start.strftime("%Y.%m.%d") if multi_year else start.strftime("%m/%d")
    gran = t.get("granularity")
    if gran == "minute":
        clock = start.strftime("%H:%M")
    elif gran == "hour":
        if end and end.date() > start.date():
            # 자정을 넘는 구간 — "20~0시" 가 아니라 "20~24시", "22시~익일 1시"로 적는다
            clock = f"{start.hour}~24시" if end.hour == 0 else f"{start.hour}시~익일 {end.hour}시"
        else:
            clock = f"{start.hour}~{end.hour}시" if end and end.hour != start.hour else f"{start.hour}시"
        if t.get("approximate"):
            clock += "경"
    else:
        clock = ""
    if gran == "month":
        day = start.strftime("%Y.%m")
    if gran == "year":
        day = start.strftime("%Y")
    return f"{day}\n{clock}" if multi_year and clock else f"{day} {clock}".strip()


# 타임라인 줄에 쓰는 짧은 이름.
#
# 없는 말을 지어내지 않는다 — 원문에서 덜어내기만 한다. 왼쪽 칸에 이미 날짜가 있으니
# 앞머리 날짜를 떼고, 여러 문장이면 첫 문장만 남긴다. 전문은 '자세히'에서 보여준다.
_LEAD_DATE = re.compile(
    r"^(?:\d{2,4}\s*[.년]\s*)?\d{1,2}\s*[./월]\s*\d{1,2}\s*[.일]?\s*"
    r"(?:\d{1,2}\s*시(?:\s*\d{1,2}\s*분)?(?:경|쯤)?\s*)?"
    r"(?:새벽|아침|낮|저녁|밤|오전|오후)?\s*"
)


def _short_title(title: str) -> str:
    """타임라인 한 줄에 적을 문장.

    앞머리의 날짜는 뗀다 — 날짜는 왼쪽 칸에 이미 있다. 여러 문장이면 첫 문장만.

    **길이로 자르지는 않는다.** 여기서 잘라 '…' 를 붙이면 화면이 아무리 넓어도
    끝까지 안 보인다. 자리에 맞춰 줄이는 일은 화면(CSS)이 한다.
    """
    text = _LEAD_DATE.sub("", title.strip(), count=1).strip()
    if len(text) < 2:
        text = title.strip()
    first = re.split(r"(?<=[.!?])\s+", text)[0].strip()
    if len(first) >= 2:
        text = first
    return text.rstrip(" .")


def _full_text(event: dict[str, Any]) -> str:
    """'자세히'에 보여줄 원문.

    엔진이 만든 제목은 긴 문장을 '…' 로 줄여 놓는다. 줄인 제목이면 같은 문장을
    담고 있는 출처 인용으로 되살린다 — 자세히를 눌렀는데 또 잘려 있으면 안 된다.
    """
    title = event["title"]
    quotes = [s["quote"] for s in event["sources"] if s.get("quote")]
    if not title.endswith("…"):
        return title
    stem = title[:-1].strip()[:12]
    candidates = [q for q in quotes if stem and q.startswith(stem)] or quotes
    if not candidates:
        return title
    longest = max(candidates, key=len)
    return longest if len(longest) > len(title) else title


def _source_line(sources: list[dict[str, Any]], doc_index: dict[str, int], docs: dict[str, dict]) -> str:
    if not sources:
        return "뒷받침하는 자료가 없어요"
    s = sources[0]
    doc_id = s["source_doc_id"]
    idx = doc_index.get(doc_id, 0)
    mark = CIRCLED[idx] if idx < len(CIRCLED) else f"({idx + 1})"
    name = docs.get(doc_id, {}).get("file_name", doc_id)
    text = f"출처 {mark}  {name} · {s['source_line']}줄"
    if len(sources) > 1:
        text += f" 외 {len(sources) - 1}곳"
    return text


def _timeline(result: dict[str, Any], docs: dict[str, dict], doc_index: dict[str, int]) -> list[dict[str, Any]]:
    tl = result["timeline"]
    events = tl["events"]
    starts = [_dt(t["start"]) for e in events if (t := e.get("time") or {}).get("start")]
    multi_year = bool(starts) and max(starts).year != min(starts).year

    conflict_sources = {
        (s["source_doc_id"], s["source_line"])
        for issue in result["analysis"]["issues"]
        if issue["category"] == "inconsistency"
        for s in issue["sources"]
    }

    rows: list[tuple[datetime, dict[str, Any]]] = []
    for e in events:
        time = e.get("time") or {}
        flags = set(e.get("flags") or [])
        level = e.get("evidence_level")
        if level == "record":
            kind, badge = "verified", "확인됨"
        elif level == "user":
            kind, badge = "mine", "내가 입력"
        else:
            kind, badge = "claim", "주장 · 미확인" if "claim_only" in flags else "미확인"
        conflict = any((s["source_doc_id"], s["source_line"]) in conflict_sources for s in e["sources"])
        start = _dt(time.get("start")) or datetime.max
        rows.append((start, {
            "type": "event",
            "time": "시각 미상" if e.get("time_unknown") or not time else _event_time(time, multi_year),
            # 줄 이름은 잘리지 않은 원문에서 뽑는다 — 엔진이 '…' 로 줄여 둔 제목에서
            # 뽑으면 화면이 아무리 넓어도 그 자리에서 끝난다
            "title": _short_title(_full_text(e)),
            "full": _full_text(e),
            "kind": kind,
            "badge": badge,
            "conflict": conflict,
            "needs_date": bool(time.get("needs_confirmation")),
            "source": _source_line(e["sources"], doc_index, docs),
            "sources": [
                {
                    "name": docs.get(s["source_doc_id"], {}).get("file_name", s["source_doc_id"]),
                    # 화면 서버가 이것으로 올린 원본을 찾아 준다
                    "doc_id": s["source_doc_id"],
                    "line": s["source_line"],
                    "quote": s.get("quote"),
                }
                for s in e["sources"]
            ],
        }))

    for g in tl.get("gaps") or []:
        start, end = _dt(g["start"]), _dt(g["end"])
        years = g["hours"] / 24 / 365
        span = f"약 {years:.1f}년" if years >= 1 else f"약 {round(g['hours'] / 24)}일"
        rows.append((start, {
            "type": "gap",
            "range": f"{start:%Y.%m.%d} – {end:%Y.%m.%d}",
            "text": f"이 기간의 기록이 없어요 ({span})",
        }))

    rows.sort(key=lambda r: r[0])
    return [r[1] for r in rows]


def _issues(result: dict[str, Any], docs: dict[str, dict]) -> list[dict[str, Any]]:
    groups = []
    for category, label, severity in ISSUE_GROUPS:
        items = []
        for issue in sorted(result["analysis"]["issues"], key=lambda i: i["priority"]):
            if issue["category"] != category:
                continue
            if issue["sources"]:
                s = issue["sources"][0]
                how = f"근거 · {docs.get(s['source_doc_id'], {}).get('file_name', s['source_doc_id'])} {s['source_line']}줄"
            elif issue["checked_doc_ids"]:
                how = f"확인한 자료 {len(issue['checked_doc_ids'])}개에서 찾지 못함"
            else:
                how = ""
            items.append({"text": issue["message"], "how": how})
        if items:
            groups.append({"label": label, "severity": severity, "items": items})
    return groups


def _slot_value(value: Any) -> str:
    """엔진 값을 사람이 읽는 꼴로. 단위를 붙이거나 뜻을 바꾸지는 않는다."""
    text = str(value)
    if text in {"True", "true"}:
        return "예"
    if text in {"False", "false"}:
        return "아니오"
    if text.isdigit() and len(text) > 3:
        return f"{int(text):,}"
    return text


def _people(result: dict[str, Any], docs: dict[str, dict]) -> list[dict[str, Any]]:
    """인물 · 관계 탭. 엔진이 합치지 못하고 남긴 '같은 사람일 수 있음'까지 그대로 보여준다."""
    entities = result["timeline"]["entities"]
    by_id = {e["entity_id"]: e for e in entities}

    # 어느 자료에 나온 이름인지 — claim 의 화자와 timeline 이벤트 참가자에서 모은다
    seen: dict[str, set[str]] = {}
    for event in result["timeline"]["events"]:
        for entity_id in event.get("participant_entity_ids", []):
            for s in event.get("sources", []):
                seen.setdefault(entity_id, set()).add(s["source_doc_id"])

    groups = []
    for kind, label in ENTITY_GROUPS:
        members = []
        for e in entities:
            if e["kind"] != kind:
                continue
            links = [
                {
                    "name": by_id.get(link["other_entity_id"], {}).get("canonical_name", link["other_entity_id"]),
                    "reason": link["reason"],
                }
                for link in e.get("possible_same_as", [])
            ]
            members.append({
                "name": e["canonical_name"],
                "roles": e.get("roles", []),
                "docs": sorted(docs.get(d, {}).get("file_name", d) for d in seen.get(e["entity_id"], set())),
                "same_as": links,
            })
        if members:
            groups.append({"label": label, "items": members})
    return groups


def _slots(result: dict[str, Any], docs: dict[str, dict]) -> list[dict[str, Any]]:
    """주장 대조 탭. 한 항목을 자료마다 뭐라고 적었는지 나란히 놓는다."""
    claims = result["extraction"]["claims"]
    rows = []
    for status in result["analysis"]["slot_statuses"]:
        slot = status["slot"]
        state_label, severity = SLOT_STATES.get(status["state"], (status["state"], "unknown"))
        said = []
        for c in claims:
            if c.get("slot") != slot or c.get("slot_value") is None:
                continue
            doc = docs.get(c["doc_id"], {})
            said.append({
                "value": _slot_value(c["slot_value"]),
                "doc": doc.get("file_name", c["doc_id"]),
                "speaker": c.get("speaker") or "",
                "record": c.get("evidence_level") == "record",
            })
        rows.append({
            "slot": SLOT_LABELS.get(slot, slot),
            "value": status.get("value"),
            "state": state_label,
            "severity": severity,
            "said": said,
        })
    return rows


def _period(result: dict[str, Any]) -> str:
    starts = sorted(d for e in result["timeline"]["events"] if (d := _dt((e.get("time") or {}).get("start"))))
    if not starts:
        return ""
    a, b = starts[0], starts[-1]
    if a.year != b.year:
        return f"{a:%Y.%m} – {b:%Y.%m}"
    return f"{a:%Y.%m.%d} – {b:%m.%d}"


def _action(card, hit, result: dict[str, Any]) -> dict[str, Any] | None:
    """행동 하나를 화면 dict 로. 준비물·제출처는 그 행동에 맞춰 다시 대조한다.

    다음 행동 하나만이 아니라 후보 전부를 이렇게 만들어 둔다. 사용자가 '냈어요'를
    누르면 화면이 다음 순위로 갈아 끼우는데, 그때도 무엇을·어디에가 비면 안 된다.
    """
    from action_engine.checklist import build_checklist

    if not hit:
        return None
    reasons = {i.code: i.reason for i in card.inf}
    why = next((reasons[c] for c in hit.codes if c in reasons), hit.why)

    deadline = next((t for t in card.tim if t.code in hit.codes and t.due_date), None)
    due = None
    if deadline:
        due = {
            "label": f"D-{deadline.days_left}" if deadline.days_left >= 0 else "기한 지남",
            "text": f"{deadline.due_date:%Y.%m.%d}까지 ({deadline.label})",
            "severity": deadline.severity,
        }

    rows: list[dict[str, str]] = []
    c = build_checklist(hit.action, result.get("documents", []), card.tim, st=card.st.code)
    state = "unresolved"
    note = None
    prepare = None
    if c and c.no_submission:
        state, note = "no_submission", c.no_submission
    elif c and c.items:
        state = "filled"
        if c.form_name:
            rows.append({"k": "무엇을", "v": c.form_name})
        if c.submit_to:
            rows.append({"k": "어디에", "v": c.submit_to})
        if due:
            rows.append({"k": "언제까지", "v": due["text"]})
        if c.statute:
            rows.append({"k": "근거", "v": c.statute})
        prepare = {
            "done": c.done,
            "total": c.total,
            "items": [{"label": i.label, "state": i.state, "required": i.required} for i in c.items],
        }
        note = c.advisory or c.prerequisite

    return {
        "rule_no": hit.rule_no,
        "action": hit.action,
        "label": ACTION_LABELS.get(hit.action, hit.action),
        "why": why,
        "rule_why": hit.why,
        "due": due,
        "state": state,
        "rows": rows,
        "prepare": prepare,
        "note": note,
        "unverified": card.requirements_status == "draft_unverified",
        "also": [{"rule_no": a.rule_no, "action": a.action, "label": ACTION_LABELS.get(a.action, a.action), "why": a.why}
                 for a in card.also],
        # 낸 것을 기록하는 자리. 제출처는 지식베이스 값이 있을 때만 채운다.
        "submit_to": c.submit_to if c else None,
        "form_name": c.form_name if c else None,
        # 낼 서류가 정해진 행동에만 초안이 붙는다
        "draft": _draft(card, result, hit.action),
    }


# 「회신 왔어요」에서 고를 수 있는 결정 내용.
# mapping.DECISION_TABLE 이 읽을 수 있는 말만 둔다 — 표에 없는 말을 고르게 해 놓고
# 아무 일도 일어나지 않으면 사용자는 기능이 고장 난 줄 안다.
RESPONSE_CHOICES = ["불송치", "불기소", "항고 기각", "피의자중지", "참고인중지", "기소"]


def _outcomes(case_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """결정 내용마다 사건이 어떻게 달라지는지 미리 계산해 둔다.

    화면은 정적 파일이라 엔진을 부를 수 없다. 그래서 고를 수 있는 답마다 엔진을 한 번씩
    돌려 결과를 실어 보낸다. 화면이 규칙을 흉내 내는 것이 아니라 엔진이 낸 답을 고르는 것이다.
    """
    from datetime import date as _date

    from action_engine import Submission, SubmissionResponse

    out: dict[str, Any] = {}
    received = _date.fromisoformat(result["as_of"])   # 기준일에 받았다고 두고 계산한다
    for choice in RESPONSE_CHOICES:
        sub = Submission(
            submission_id="preview", action="ACT-회신", submitted_at=received,
            response=SubmissionResponse(received_at=received, decision_type=choice),
        )
        card = build_card(result, [sub])
        live = [t for t in card.tim if t.due_date]
        out[choice] = {
            "st": card.st.label,
            "next": ACTION_LABELS.get(card.next_action.action, card.next_action.action) if card.next_action else None,
            # 화면이 actions 목록에서 이 행동을 찾아 그대로 그린다
            "next_key": card.next_action.action if card.next_action else None,
            # 날짜는 굳히지 않고 기간만 넘긴다 — 사용자가 고른 통지 수령일로 화면이 더한다.
            # (엔진이 하는 계산과 같다: 기한 = 통지 수령일 + period_days)
            "deadlines": [{
                "label": t.label,
                "period_days": t.period_days,
                "statute": t.statute,
                "submit_to": t.submit_to,
            } for t in live],
        }
    return out


def _draft(card, result: dict[str, Any], action: str | None) -> dict[str, Any] | None:
    """낼 서류의 초안. 만들 서류가 정해져 있지 않으면 화면도 아무것도 그리지 않는다."""
    from action_engine.draft import build_draft

    from action_engine.polish import polish

    d = build_draft(result, card, action=action)
    if not d:
        return None

    # 문장으로 엮는 것은 선택이다. 키가 없거나 검사에 걸리면 골격만 싣는다 —
    # 화면은 둘 다 그릴 줄 알아야 하고, 없다고 비지 않는다.
    prose = polish(d)
    if prose.rejected:
        print(f"  {action}: 문장 다듬기를 건너뜁니다 — {prose.rejected}")

    return {
        "is_draft": d.is_draft,
        "prose": prose.text,
        "form_name": d.form_name,
        "form_source": d.form_source,
        "form_url": d.form_url,
        "fields": [{"label": f.label, "value": f.value, "from": f.filled_from} for f in d.fields],
        "unfilled": [{"label": f.label, "reason": f.reason} for f in d.unfilled],
        "sections": [{
            "heading": sec.heading,
            "note": sec.note,
            "lines": [{
                "date": ln.date,
                "text": ln.text,
                "level": ln.evidence_level,
                "source": (lambda c: (c.file_name or c.doc_id) + (f" {c.line}줄" if c.line else ""))(ln.citations[0]),
            } for ln in sec.lines],
        } for sec in d.sections],
        "dropped": d.dropped,
    }


def _actions(card, result: dict[str, Any]) -> list[dict[str, Any]]:
    """다음 행동 후보를 우선순위 순서로. 첫 줄이 지금의 다음 행동이다."""
    hits = ([card.next_action] if card.next_action else []) + list(card.also)
    return [a for a in (_action(card, hit, result) for hit in hits) if a]


def build_view(case_id: str, title: str, result: dict[str, Any]) -> dict[str, Any]:
    card = build_card(result)
    docs = {d["doc_id"]: d for d in result["documents"]}
    evidence = [d for d in result["documents"] if d["doc_type"] != "user_note"]
    doc_index = {d["doc_id"]: i for i, d in enumerate(evidence)}
    as_of = date.fromisoformat(result["as_of"])
    return {
        "id": case_id,
        "title": title,
        # 화면이 사건 유형별로 카드 색을 묶는 데 쓴다 — 사람이 읽는 이름과 따로 내보낸다
        "type": card.case_type,
        "type_label": card.case_type_label,
        "as_of": f"{as_of:%Y.%m.%d}",
        "period": _period(result),
        "doc_count": card.evidence_doc_count,
        "need_count": card.needs_confirmation_count,
        "stages": _stages(card),
        # doc_id 를 같이 싣는다 — 화면 서버가 이것으로 올린 원본 파일을 찾아 준다.
        # 파일 이름은 겹칠 수 있어 이름으로 찾으면 엉뚱한 자료를 열어 준다.
        "sources": [{"kind": _kind(d["file_name"], d["doc_type"]), "name": d["file_name"], "doc_id": d["doc_id"]}
                    for d in evidence],
        "timeline": _timeline(result, docs, doc_index),
        "people": _people(result, docs),
        "slots": _slots(result, docs),
        "issues": _issues(result, docs),
        "next_action": _action(card, card.next_action, result),
        # 화면이 '냈어요'를 기록하면 이 목록에서 다음 순위를 꺼내 쓴다
        "actions": _actions(card, result),
        # 「회신 왔어요」에서 답을 고르면 이 표에서 그 답의 결과를 꺼내 쓴다
        "response_choices": RESPONSE_CHOICES,
        "outcomes": _outcomes(case_id, result),
    }


def _extra() -> list[tuple[str, str, Path]]:
    """직접 만든 사건 목록. 파일이 없으면 빈 목록 — 지금까지와 똑같이 돈다."""
    if not EXTRA_CASES.exists():
        return []
    rows = json.loads(EXTRA_CASES.read_text(encoding="utf-8"))
    out = []
    for row in rows:
        path = Path(row["result"])
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise SystemExit(f"{EXTRA_CASES.name}: {row['result']} 를 찾지 못했습니다 — 엔진을 먼저 돌리세요")
        out.append((row["id"], row["title"], path))
    return out


def build_all() -> list[dict[str, Any]]:
    views = []
    for case_id, title in CASES:
        result = json.loads((FIXTURES / f"{case_id}.json").read_text(encoding="utf-8"))
        views.append(build_view(case_id, title, result))
    for case_id, title, path in _extra():
        views.append(build_view(case_id, title, json.loads(path.read_text(encoding="utf-8"))))
    return views


def render(views: list[dict[str, Any]]) -> str:
    body = json.dumps(views, ensure_ascii=False, indent=2)
    return (
        "// 자동 생성 파일 — action-engine/tools/export_web.py 로 다시 만든다. 직접 고치지 않는다.\n"
        f"window.TARAE_CASES = {body};\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="화면 데이터 만들기")
    parser.add_argument("--result", help="research-engine 출력 하나 — 주면 그 사건 하나만 --out 에 쓴다")
    parser.add_argument("--id")
    parser.add_argument("--title")
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.result:
        if not (args.id and args.title and args.out):
            parser.error("--result 에는 --id · --title · --out 이 함께 필요합니다")
        view = build_view(args.id, args.title, json.loads(Path(args.result).read_text(encoding="utf-8")))
        Path(args.out).write_text(json.dumps(view, ensure_ascii=False), encoding="utf-8")
        return

    views = build_all()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(views), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} — 사건 {len(views)}건")


if __name__ == "__main__":
    main()
