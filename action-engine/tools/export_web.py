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
from action_engine.mapping import effective_issuer

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
OUT = ROOT / "web" / "data" / "cases.js"

# 화면에 올릴 예시 사건. 픽스처에는 사용자가 붙인 사건 이름이 없어 여기서 준다(인물·사건은 가상).
CASES = [
    ("used_goods_fraud", "중고거래 사기 피해"),
    ("long_unsolved_missing", "2015년 실종 사건"),
    ("suspension_recent", "고소 사건 (수사중지)"),
]

# 픽스처 세 건은 테스트가 직접 참조해서 계속 둔다(위 CASES). 다만 지금은 화면에는 올리지 않는다 —
# 심사용 화면은 시연 사건(EXTRA_CASES) 하나로 좁혔다. 다시 올리려면 여기서 뺀다.
SKIP_ON_SCREEN = {"used_goods_fraud", "long_unsolved_missing", "suspension_recent"}

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
    "ACT-진행확인": "수사 진행상황 확인",
    "ACT-재판단계": "재판 단계 — 이 서비스의 안내 범위 밖",
}

ISSUE_GROUPS = [
    ("inconsistency", "자료 간 모순", "conflict"),
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
    "offence": "죄명",
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
    "unreadable": ("읽히지 않음", "unverified"),
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


def _stages(card) -> list[dict[str, Any]]:
    engine = {s["stage"]: s["state"] for s in card.stages}
    # 직접 적은 메모로만 이른 단계 — 진행은 보여 주되 자료로 확인된 단계와 구별한다
    noted = {s["stage"] for s in card.stages if s.get("noted_only")}
    track = STAGE_TRACKS.get(card.case_type)
    if not track:
        # 유형별 이름을 정하지 않은 사건은 엔진 단계를 그대로 쓴다
        return [{"label": s["label"], "state": {"done": "done", "current": "current"}.get(s["state"], "todo"),
                 "noted": s["stage"] in noted}
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
        reached = [c for c in codes if engine.get(c) in ("done", "current")]
        rows.append({"label": label, "state": state, "noted": bool(reached) and all(c in noted for c in reached)})
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


# ── 타임라인 줄 이름: 무슨 일이 있었는가 ────────────────────────────────
#
# 원문 한 줄을 그대로 붙이면 '위 대상물은 … 등록을 위하여' 처럼 무슨 일인지 알 수 없는
# 문장이 뜬다. 그래서 자료의 종류와 행위로 짧게 요약한다.
#
# 요약에 쓰는 말은 아래 표에서만 고른다. 장소 · 이름 · 금액은 그 줄에 적힌 값을 옮길 뿐이다.
# 표에 없는 일은 지어내지 않고 원문 첫 문장으로 둔다. 원문은 '자세히'(full)에 그대로 있다.

def _flat(text: str) -> str:
    """OCR 이 글자 사이에 넣은 빈칸을 뗀다 ('실 종 신 고' → '실종신고')."""
    return re.sub(r"\s+", "", text)


# 결정 내용. 앞의 것이 더 구체적이다 — '참고인중지'가 '수사중지'보다 먼저다.
_DECISIONS = [
    ("참고인중지", "수사중지(참고인중지)"), ("피의자중지", "수사중지(피의자중지)"), ("수사중지", "수사중지"),
    ("기소중지", "기소중지"), ("불송치", "불송치"), ("불기소", "불기소"), ("기소유예", "기소유예"),
    ("혐의없음", "혐의없음"), ("공소권없음", "공소권없음"), ("죄가안됨", "죄가안됨"), ("각하", "각하"),
]
_DECISION_LINE = re.compile(r"결정|처분|주문|사유|내용")


def _decision(lines: list[str]) -> str | None:
    """결정 내용. '결정·처분' 이 적힌 줄을 먼저 보고, 없으면 문서 전체에서 찾는다."""
    labelled = [_flat(t) for t in lines if _DECISION_LINE.search(_flat(t))]
    for pool in (labelled, [_flat(t) for t in lines]):
        text = " ".join(pool)
        for word, label in _DECISIONS:
            if word in text:
                return label
    return None


# 사람이 쓴 글은 양식이 아니다 — 메모 둘째 줄의 '실종신고'를 문서 제목으로 읽으면 안 된다
_NARRATIVE = {"memo", "statement", "complaint", "news", "messenger", "transcript", "user_note"}


def _doc_label(doc: dict[str, Any]) -> str | None:
    """정해진 양식(접수증 · 통지서 · 확인서)이면 그 문서가 뜻하는 일. 양식이 아니면 None."""
    if doc.get("doc_type") in _NARRATIVE:
        return None
    lines = [ln["text"] for ln in doc.get("lines", [])]
    head, body = _flat(" ".join(lines[:2])), _flat(" ".join(lines))  # 제목은 맨 위 한두 줄에 있다
    if re.search(r"유전자|DNA", head, re.I):
        if re.search(r"결과|감정", head):
            return "DNA 검사 결과"
        if "채취" in head:
            return "DNA 채취 — 실종자 유전자 등록" if re.search(r"프로파일링|실종아동", body) else "DNA 채취"
        return "DNA 검사"
    if "실종신고" in head:
        return "실종신고 접수"
    if "사이버범죄" in head and "접수" in head:
        return "사이버범죄 신고 접수"
    if re.search(r"접수증|접수확인", head):
        return "사건 접수"
    if "진행상황" in head:
        return "수사 진행상황 통지" + (" — 사건 재배당" if "재배당" in body else "")
    if re.search(r"통지서|결정서", head) and re.search(r"수사|결정|처분|결과", head):
        decision = _decision(lines)
        return f"수사결과 통지 — {decision}" if decision else "수사결과 통지"
    return None


# 장소: 숫자 없는 낱말 한두 개가 장소 꼬리말로 끝나는 자리 ('○○천 제방길', '○○시장 입구')
_PLACE = re.compile(
    r"(?<!\S)((?:(?![^\s]*(?:쯤|경|오전|오후|밤|낮|새벽|저녁|아침)\s)[^\s\d,.:;|ㅣ()]+\s)?[^\s\d,.:;|ㅣ()]*(?:역|천|길|시장|공원|골목|하류|갈대밭|편의점|터미널|정류장|아파트)"
    r"(?:\s?(?:입구|앞|인근|근처))?)(?=에서|에|\s|$)"
)
_FOUND = re.compile(r"([가-힣]+?)(?:이|가)\s*발견")
_AGENCY = re.compile(r"([^\s,.]*(?:경찰서|수사대|지구대|파출소|경찰청|검찰청|지청))")


def _place(text: str) -> str | None:
    m = _PLACE.search(text)
    return m.group(1).strip() if m else None


def _line_people(result: dict[str, Any], source: dict[str, Any]) -> list[str]:
    names = {
        m["normalized"] or m["name"]["value"]
        for m in result["extraction"]["mentions"]
        if m["kind"] == "person" and m["doc_id"] == source["source_doc_id"]
        and m["name"]["source_line"] == source["source_line"]
    }
    return sorted(names)


def _event_label(e: dict[str, Any], kinds: set[str], text: str, result: dict[str, Any]) -> str | None:
    """한 줄에 적힌 행위로 요약한다. 표에 없는 행위면 None."""
    flat = _flat(text)
    stage = e["stage"]
    if "sighting" in kinds:
        label = "마지막 목격" if re.search(r"마지막|최종", flat) else "목격"
        where = _place(text)
        return f"{label} · {where}" if where else label
    if (found := _FOUND.search(text)) and stage == "occurrence":
        return f"{found.group(1)} 발견"
    if "contact_lost" in kinds:
        return "연락 두절"
    if "disappearance" in kinds:
        people = _line_people(result, e["sources"][0]) if e["sources"] else []
        return f"{people[-1]} 실종" if len(people) == 1 else "실종"
    amount = e.get("amount")
    amount = amount.get("value") if isinstance(amount, dict) else amount
    if "fraud" in kinds:
        return f"{amount:,}원 사기 피해" if isinstance(amount, int) else "사기 피해"
    if "violence" in kinds:
        return "폭행 피해"
    if "harm" in kinds:
        return "피해"
    if "dealing" in kinds:
        return "거래 대화"
    if "petition" in kinds or stage == "report":
        for word, label in (("재수사", "재수사 요청"), ("이의신청", "이의신청"), ("재기신청", "재기신청"),
                            ("실종신고", "실종신고"), ("고소", "고소"), ("고발", "고발"), ("진정", "진정"),
                            ("112", "112 신고"), ("신고", "신고")):
            if word in flat:
                agency = _AGENCY.search(text) if label in ("고소", "고발", "진정", "신고") else None
                return f"{agency.group(1).rstrip('에')} {label}" if agency else label
        return None
    if stage == "transfer":
        return f"{amount:,}원 송금" if isinstance(amount, int) else "송금"
    if stage == "receipt":
        return "사건 접수"
    if stage == "investigation":
        for pattern, label in ((r"재배당", "사건 재배당"), (r"조사를?받은.{0,6}없|조사를?받지않", "경찰 조사를 받지 않았다는 진술"),
                               (r"초동수사|수사가?늦어", "수사가 늦었다는 주장"), (r"압수|수색", "압수 · 수색"),
                               (r"소환|출석", "출석 조사"), (r"입건", "입건"), (r"(?<!불)송치", "검찰 송치")):
            if re.search(pattern, flat):
                return label
        return None
    if stage == "outcome":
        decision = _decision([text])
        return f"수사결과 — {decision}" if decision else None
    return None


def _summary(e: dict[str, Any], result: dict[str, Any], docs: dict[str, dict]) -> str | None:
    """타임라인 한 줄 이름. 요약할 수 없으면 None — 부른 쪽이 원문 첫 문장을 쓴다."""
    if not e["sources"]:
        return None
    source = e["sources"][0]
    doc = docs.get(source["source_doc_id"], {})
    if doc.get("doc_type") == "user_note" or e.get("evidence_level") == "user":
        return None  # 본인이 직접 적은 말은 그대로 둔다
    by_id = {x["event_id"]: x for x in result["extraction"]["events"]}
    kinds = {k for i in e.get("event_ids", []) if (k := (by_id.get(i) or {}).get("action_kind"))}
    text = _full_text(e)

    # 양식 문서의 줄은 그 문서가 뜻하는 일이다. 다만 발급일과 다른 날의 일
    # (접수증의 '최종목격 11/4 23:20')은 그 줄에 적힌 일로 요약한다.
    label = _doc_label(doc) if doc else None
    if label:
        issued = ((result["extraction"].get("document_dates") or {}).get(doc["doc_id"]) or {}).get("value") or {}
        when, day = (e.get("time") or {}).get("start"), issued.get("start")
        if source["source_line"] <= 2 or not when or (day and when[:10] == day[:10]):
            return label
    return _event_label(e, kinds, text, result)


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
            # 화면이 '낸 것 · 받은 답'을 날짜 순서대로 끼워 넣을 때 쓴다. 시각을 모르면 없다
            "at": f"{start:%Y-%m-%d}" if start != datetime.max else None,
            "time": "시각 미상" if e.get("time_unknown") or not time else _event_time(time, multi_year),
            # 무슨 일이었는지 요약한 이름. 요약할 수 없으면 잘리지 않은 원문의 첫 문장 —
            # 엔진이 '…' 로 줄여 둔 제목에서 뽑으면 화면이 아무리 넓어도 그 자리에서 끝난다
            "title": _summary(e, result, docs) or _short_title(_full_text(e)),
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
            "at": f"{start:%Y-%m-%d}",
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
            # '차이가 있어 보이지만 판단 근거가 부족한' 것도 어긋남 묶음에 둔다 — 엔진은 확인되지 않음으로
            # 분류하지만, 자료끼리 다른 곳을 짚는 것이 이 서비스의 강점이라 묻히면 안 된다. 문장이 '보이지만'
            # 으로 단정하지 않으므로 묶음만 옮긴다.
            shown = "inconsistency" if issue.get("condition") == "suspected_conflict" else issue["category"]
            if shown != category:
                continue
            if issue["sources"]:
                s = issue["sources"][0]
                how = f"근거 · {docs.get(s['source_doc_id'], {}).get('file_name', s['source_doc_id'])}"
            elif issue["checked_doc_ids"]:
                how = f"확인한 자료 {len(issue['checked_doc_ids'])}개에서 찾지 못함"
            else:
                how = ""
            items.append({"text": _plain(issue["message"], docs), "how": how, "kind": issue["condition"]})
        if items:
            groups.append({"label": label, "severity": severity, "items": items})
    return groups


ASCII_ID = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_]*(?![A-Za-z0-9_])")
# 엔진 문장이 출처로 붙이는 줄 번호 — '통지서.jpg · 8줄' 의 '· 8줄'. 화면은 자료 이름까지만 보여 준다.
LINE_NO = re.compile(r"\s*·\s*\d+줄")


def _drop_score_note(message: str) -> str:
    """끝에 붙은 엔진 판정 근거 괄호 — "(모순 점수 0.54 < 기준 0.70; … (0.60))" — 를 뗀다. 괄호가 겹칠 수 있다."""
    text = message.rstrip()
    if not text.endswith(")"):
        return message
    depth = 0
    for i in range(len(text) - 1, -1, -1):
        depth += {")": 1, "(": -1}.get(text[i], 0)
        if depth == 0:
            return text[:i].rstrip() if "기준 " in text[i:] else message
    return message


def _plain(message: str, docs: dict[str, dict]) -> str:
    """엔진 문장을 화면 말로 — 점수 괄호와 줄 번호를 떼고, 자료 id 는 올린 파일 이름으로 바꾼다."""
    message = _drop_score_note(message)
    message = LINE_NO.sub("", message)
    return ASCII_ID.sub(lambda m: docs[m.group(0)].get("file_name", m.group(0)) if m.group(0) in docs else m.group(0),
                        message)


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


def _action(card, hit, result: dict[str, Any], prose: bool = True) -> dict[str, Any] | None:
    """행동 하나를 화면 dict 로. 준비물·제출처는 그 행동에 맞춰 다시 대조한다.

    다음 행동 하나만이 아니라 후보 전부를 이렇게 만들어 둔다. 사용자가 '냈어요'를
    누르면 화면이 다음 순위로 갈아 끼우는데, 그때도 무엇을·어디에가 비면 안 된다.
    """
    from action_engine.checklist import build_checklist

    if not hit:
        return None
    reasons = {i.code: i.reason for i in card.inf}
    why = next((reasons[c] for c in hit.codes if c in reasons), hit.why)
    why = _plain(why, {d["doc_id"]: d for d in result.get("documents", [])})

    deadline = next((t for t in card.tim if t.code in hit.codes and t.due_date), None)
    due = None
    if deadline:
        due = {
            "label": f"D-{deadline.days_left}" if deadline.days_left >= 0 else "기한 지남",
            "text": f"{deadline.due_date:%Y.%m.%d}까지 ({deadline.label})",
            "severity": deadline.severity,
        }

    rows: list[dict[str, str]] = []
    c = build_checklist(hit.action, result.get("documents", []), card.tim, st=card.st.code, issuer=effective_issuer(card.st))
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
        "draft": _draft(card, result, hit.action, prose=prose),
    }


# 「회신 왔어요」에서 고를 수 있는 결정 내용.
# mapping.DECISION_TABLE 이 읽을 수 있는 말만 둔다 — 표에 없는 말을 고르게 해 놓고
# 아무 일도 일어나지 않으면 사용자는 기능이 고장 난 줄 안다.
RESPONSE_CHOICES = ["불송치", "불기소", "항고 기각", "피의자중지", "참고인중지", "기소"]


def _severity_days() -> dict[str, int]:
    from action_engine.rules import load_deadlines

    bands = load_deadlines()["severity"]
    return {"critical": bands["critical_days"], "soon": bands["soon_days"]}


def _from_notice() -> set[str]:
    """통지 수령일(decision_time)을 기산일로 쓰는 기한 코드."""
    from action_engine.rules import load_deadlines

    return {row["code"] for row in load_deadlines()["deadlines"] if row.get("basis") == "decision_time"}


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
        # 통지 수령일부터 세는 기한만 싣는다 — 화면이 사용자가 고른 수령일에 기간을 더하기 때문이다.
        # 공소시효는 범행 종료일부터 센다. 수령일에 10년을 더하면 엉뚱한 만료일이 나온다.
        live = [t for t in card.tim if t.due_date and t.code in _from_notice()]
        out[choice] = {
            "st": card.st.label,
            # 이 답을 받았을 때의 행동 목록 — 무엇을 · 어디에가 새 단계에 맞춰 다시 대조돼 있다.
            # (불기소를 받으면 '불복'은 이의제기서가 아니라 항고장이다. 옛 카드의 행을 쓰면 안 된다.)
            "actions": _answer_actions(card, result),
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


def _action_tims(action: str) -> set[str]:
    """그 행동을 부르는 규칙이 보는 기한 코드. 단계로 발화한 규칙(5번)은 근거 코드에 기한이 없어서 쓴다."""
    from action_engine.rules import load_rules

    codes: set[str] = set()

    def walk(when: dict[str, Any]) -> None:
        codes.update(when.get("tim_code", []))
        for sub in when.get("any", []):
            walk(sub)

    for rule in load_rules()["rules"]:
        if rule["action"] == action:
            walk(rule.get("when") or {})
    return codes


def _unmark_new_notice(view: dict[str, Any]) -> None:
    """새로 받은 답의 통지서는 자료함에 없다 — 옛 통지서가 있다고 '보유'로 두지 않는다.

    자료함의 통지서는 이전 결정(예: 수사중지)의 것이다. 불기소를 받았다고 기록했을 뿐 그 통지서를
    올리지 않았는데 '불기소 이유 통지서 — 보유'로 보이면, 없는 서류를 가진 줄 알고 준비하지 않는다.
    """
    prepare = view.get("prepare")
    if not prepare:
        return
    for item in prepare["items"]:
        if item["state"] == "보유" and "통지서" in item["label"]:
            item["state"] = "미보유"
    prepare["done"] = sum(1 for i in prepare["items"] if i["state"] == "보유")


def _answer_actions(card, result: dict[str, Any]) -> list[dict[str, Any]]:
    """답을 받은 뒤의 행동 목록. 기한은 날짜로 굳히지 않고 기간만 싣는다.

    미리 계산할 때는 기준일에 답을 받았다고 두지만, 실제로 받은 날은 사용자가 고른다.
    그래서 '언제까지' 행과 D-day 를 빼고 ``due_rule``(기간)을 실어 화면이 받은 날에 더하게 한다.
    """
    out = []
    for hit in ([card.next_action] if card.next_action else []) + list(card.also):
        view = _action(card, hit, result, prose=False)
        if not view:
            continue
        codes = set(hit.codes) | _action_tims(hit.action)
        deadline = next((t for t in card.tim if t.code in codes and t.period_days), None)
        view["due"] = None
        view["rows"] = [r for r in view["rows"] if r["k"] != "언제까지"]
        view["due_rule"] = {"label": deadline.label, "period_days": deadline.period_days} if deadline else None
        _unmark_new_notice(view)
        out.append(view)
    return out


def _draft(card, result: dict[str, Any], action: str | None, prose: bool = True) -> dict[str, Any] | None:
    """낼 서류의 초안. 만들 서류가 정해져 있지 않으면 화면도 아무것도 그리지 않는다.

    ``prose`` 가 False 면 문장으로 엮지 않고 골격만 싣는다 — 답마다 미리 계산하는 초안까지
    모델을 부르면 답 하나에 호출이 여러 번 늘어난다.
    """
    from action_engine.draft import build_draft

    from action_engine.polish import polish

    d = build_draft(result, card, action=action)
    if not d:
        return None

    # 문장으로 엮는 것은 선택이다. 키가 없거나 검사에 걸리면 골격만 싣는다 —
    # 화면은 둘 다 그릴 줄 알아야 하고, 없다고 비지 않는다.
    text = None
    if prose:
        polished = polish(d)
        if polished.rejected:
            print(f"  {action}: 문장 다듬기를 건너뜁니다 — {polished.rejected}")
        text = polished.text

    return {
        "is_draft": d.is_draft,
        "prose": text,
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
        # 받은 날로 기한을 다시 셀 때 화면이 쓰는 급함 기준 — 팀 기준이라 엔진의 값을 그대로 넘긴다
        "severity_days": _severity_days(),
        "outcomes": _outcomes(case_id, result),
    }


def _extra() -> list[tuple[str, str, Path, bool, bool, str | None]]:
    """직접 만든 사건 목록. 파일이 없으면 빈 목록 — 지금까지와 똑같이 돈다.

    ``"first": true`` 인 사건은 목록 맨 앞에 둔다(시연 때 처음 보이는 사건).
    ``"guide": true`` 인 사건은 화면 위에 '둘러보기 안내' 띠를 단다.
    ``"originals": "data/demo/<폴더>"`` 는 web/ 아래 원본 사진 폴더 — 자료마다 '원본 보기'를 붙인다."""
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
        out.append((row["id"], row["title"], path, bool(row.get("first")), bool(row.get("guide")), row.get("originals")))
    return out


ORIGINAL_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


def _link_originals(view: dict[str, Any], folder: str) -> None:
    """예시 사건에도 원본 사진이 있으면 자료마다 주소를 붙인다 — 로컬 서버의 with_files 와 같은 모양.

    사진은 web/<folder>/<doc_id>.<확장자> 에 둔다. 없는 자료는 주소 없이 두어 화면이 '원본 없음'으로 그린다.
    """
    base = ROOT / "web" / folder
    found = {f.stem: f for f in base.iterdir() if f.suffix.lower() in ORIGINAL_TYPES} if base.is_dir() else {}

    def mark(src: dict[str, Any]) -> None:
        f = found.get(src.get("doc_id") or "")
        if f:
            src["href"] = f"{folder}/{f.name}"
            src["media"] = ORIGINAL_TYPES[f.suffix.lower()]

    for src in view.get("sources") or []:
        mark(src)
    # 타임라인 '자세히'에서도 그 줄이 나온 원본을 바로 연다
    for row in view.get("timeline") or []:
        for src in row.get("sources") or []:
            mark(src)
    view["demo_originals"] = True


def build_all() -> list[dict[str, Any]]:
    first, views = [], []
    for case_id, title in CASES:
        result = json.loads((FIXTURES / f"{case_id}.json").read_text(encoding="utf-8"))
        views.append(build_view(case_id, title, result))
    for case_id, title, path, pinned, guide, originals in _extra():
        view = build_view(case_id, title, json.loads(path.read_text(encoding="utf-8")))
        if guide:
            view["guide"] = True
        if originals:
            _link_originals(view, originals)
        (first if pinned else views).append(view)
    return first + views


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
    screen_views = [v for v in views if v["id"] not in SKIP_ON_SCREEN]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(screen_views), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} — 사건 {len(screen_views)}건")


if __name__ == "__main__":
    main()
