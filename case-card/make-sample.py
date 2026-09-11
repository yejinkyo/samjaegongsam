"""파이프라인 결과에서 카드 화면이 쓰는 필드만 추려 index.html 의 예시 데이터 구간을 갈아끼운다.

index.html 은 의존성 없는 단일 파일로 유지한다. 그래서 별도 JSON을 두지 않고
``/* SAMPLE:BEGIN */ … /* SAMPLE:END */`` 사이를 직접 치환한다.

    cd research-engine
    uv run research-engine run tests/fixtures/long_unsolved_missing/case.json --out out/long.json
    uv run python ../case-card/make-sample.py out/long.json
"""

import json
import sys
from pathlib import Path

BEGIN = "/* SAMPLE:BEGIN"
END = "/* SAMPLE:END */"

DOC_FIELDS = ("doc_id", "file_name", "doc_type", "evidence_level")
EVENT_FIELDS = (
    "timeline_event_id", "stage", "title", "time", "time_unknown",
    "amount", "sources", "evidence_level", "needs_confirmation", "flags",
)
ISSUE_FIELDS = (
    "issue_id", "category", "condition", "message", "stage", "slot",
    "sources", "clarification_request_ids", "trigger", "priority",
)
CLARIFICATION_FIELDS = (
    "request_id", "kind", "question", "doc_id", "page", "line_no",
    "options", "context", "priority", "status", "answer",
)


def pick(obj: dict, fields) -> dict:
    return {k: obj[k] for k in fields if k in obj}


def build(d: dict) -> dict:
    tl, an = d["timeline"], d["analysis"]
    return {
        "case_id": d["case_id"],
        "case_type": d["case_type"],
        "as_of": d["as_of"],
        "documents": [pick(x, DOC_FIELDS) for x in d["documents"]],
        "clarifications": [pick(c, CLARIFICATION_FIELDS) for c in d.get("clarifications", [])],
        "timeline": {
            "current_stage": tl["current_stage"],
            "stages": tl["stages"],
            "events": [pick(e, EVENT_FIELDS) for e in tl["events"]],
            "gaps": tl["gaps"],
        },
        "analysis": {
            "case_card": an["case_card"],
            "issues": [pick(i, ISSUE_FIELDS) for i in an["issues"]],
        },
    }


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "out/long.json")
    page = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name("index.html")

    sample = build(json.loads(src.read_text(encoding="utf-8")))
    html = page.read_text(encoding="utf-8")
    i, j = html.index(BEGIN), html.index(END)
    if i > j:
        raise SystemExit("SAMPLE 마커 순서가 잘못되었습니다")

    block = (
        f"{BEGIN} — 자동 생성 구간. 손으로 고치지 말 것 (case-card/make-sample.py 로 다시 만든다)\n"
        f"   출처: {src.name} · case_type={sample['case_type']} */\n"
        f"const SAMPLE = {json.dumps(sample, ensure_ascii=False, indent=2)};\n"
    )
    page.write_text(html[:i] + block + html[j:], encoding="utf-8")

    print(
        f"{page.name} 갱신 — 문서 {len(sample['documents'])}개 · "
        f"이벤트 {len(sample['timeline']['events'])}개 · "
        f"공백 {len(sample['timeline']['gaps'])}개 · "
        f"확인 필요 {len(sample['analysis']['issues'])}건"
    )


if __name__ == "__main__":
    main()
