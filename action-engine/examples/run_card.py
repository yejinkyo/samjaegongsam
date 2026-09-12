"""사건 카드 하나를 만들어 출력한다. action-engine 이 실제로 무엇을 내놓는지 보는 용도.

    cd action-engine
    uv run python examples/run_card.py
    uv run python examples/run_card.py ../research-engine/out/long.json   # 다른 결과 파일로
"""

import json
import sys
from pathlib import Path

from action_engine import build_card

DEFAULT = Path(__file__).parent.parent / "tests" / "fixtures" / "long_unsolved_missing.json"


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not src.exists():
        raise SystemExit(f"파일이 없습니다: {src}")

    result = json.loads(src.read_text(encoding="utf-8"))   # research-engine 출력
    card = build_card(result)

    print(f"\n┌─ {card.case_type_label} " + "─" * max(0, 46 - len(card.case_type_label)))
    print(f"│  현재 단계   {card.current_stage}")
    print(f"│  확보 자료   {card.evidence_doc_count}개")
    print(f"│  완료 항목   {card.slots_done}/{card.slots_total}")
    print(f"│  확인 필요   {card.needs_confirmation_count}건")
    print("└" + "─" * 50)

    print(f"\n[절차 단계]  {card.st.code}  {card.st.label}  ({card.st.confidence})")
    print(f"             {card.st.reason}")
    if card.st.ambiguous_between:
        print(f"             ↳ 자료로 못 가름: {' 또는 '.join(card.st.ambiguous_between)}")

    print(f"\n[정보 상태]  {len(card.inf)}개")
    for h in card.inf:
        print(f"   {h.code:9} {h.label:16} {h.reason[:42]}")

    print(f"\n[기한]  {len(card.tim)}개")
    for t in card.tim:
        if t.days_left is not None:
            print(f"   {t.code:9} {t.label:18} D{t.days_left:+d} ({t.severity})")
        else:
            print(f"   {t.code:9} {t.label:18} — {t.unresolved or '기한 없음'}")

    print(f"\n[다음 행동]  규칙 {card.next_action.rule_no}번 → {card.next_action.action}")
    print(f"             {card.next_action.why}")
    print(f"             발화 코드: {', '.join(card.next_action.codes) or '(기본)'}")
    if card.also:
        print("             참고사항: " + ", ".join(f"{h.rule_no}번 {h.action}" for h in card.also))

    print("\n[절차 안내]  무엇을 · 어디에 · 어떻게 · 언제까지")
    print(f"             {card.procedure}   ← 지식베이스를 채우기 전까지 비어 있다")

    if card.checklist:
        if card.checklist.unresolved:
            print(f"\n[제출 준비물]  {card.checklist.unresolved}")
        else:
            print(f"\n[제출 준비물]  {card.checklist.done}/{card.checklist.total}")
            for i in card.checklist.items:
                print(f"   [{i.state}] {i.label}" + (f" — {i.reason}" if i.reason else ""))

    print(f"\n전체 JSON 은 {len(card.model_dump_json())} 바이트입니다. 화면은 이것만 읽으면 됩니다.\n")


if __name__ == "__main__":
    main()
