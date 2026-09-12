"""사건 카드 하나를 만들어 출력한다. action-engine 이 실제로 무엇을 내놓는지 보는 용도.

    cd action-engine
    uv run python examples/run_card.py
    uv run python examples/run_card.py ../research-engine/out/long.json   # 다른 결과 파일로

윈도우 기본 콘솔 인코딩(cp949)은 한글 박스 문자를 인코딩하지 못해 스크립트가 죽는다.
아래에서 표준출력을 UTF-8 로 바꾸고, 그래도 못 쓰는 문자는 대체 문자로 흘려보낸다.
"""

import json
import sys
from pathlib import Path

from action_engine import build_card

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT = Path(__file__).parent.parent / "tests" / "fixtures" / "long_unsolved_missing.json"
LINE = "-" * 58


def _print_agency(submit_to: str, result: dict) -> None:
    """제출처가 관계로만 적힌 경우 실제 관서명을 찾아 덧붙인다.

    '바로 위 상급경찰관서의 장'은 법령 문구 그대로라 사용자가 어디로 가야 할지 모른다.
    research-engine 은 아직 수사관서를 슬롯으로 뽑지 않으므로, 여기서는 엔티티 중
    이름이 '경찰서'로 끝나는 것을 관서로 본다. 슬롯이 생기면 그걸 쓰면 된다.
    """
    from action_engine.agencies import describe_submit_to

    station = next(
        (e.get("canonical_name") for e in result.get("timeline", {}).get("entities", [])
         if (e.get("canonical_name") or "").endswith("경찰서")),
        None,
    )
    if not station:
        return
    found = describe_submit_to(submit_to, station)
    if found.get("resolved"):
        print(f"             -> {found['target']['name']}")
        if found.get("hint"):
            print(f"             -> {found['hint']}")
    elif found.get("reason"):
        print(f"             -> {found['reason']}")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not src.exists():
        raise SystemExit(f"파일이 없습니다: {src}")

    result = json.loads(src.read_text(encoding="utf-8"))   # research-engine 출력
    card = build_card(result)

    print(f"\n{LINE}")
    print(f"  {card.case_type_label}")
    print(f"  현재 단계 {card.current_stage}   확보 자료 {card.evidence_doc_count}개   "
          f"완료 {card.slots_done}/{card.slots_total}   확인 필요 {card.needs_confirmation_count}건")
    print(LINE)

    print(f"\n[절차 단계]  {card.st.code}  {card.st.label}  ({card.st.confidence})")
    print(f"             {card.st.reason}")
    if card.st.ambiguous_between:
        print(f"             * 자료로 못 가름: {' 또는 '.join(card.st.ambiguous_between)}")

    print(f"\n[정보 상태]  {len(card.inf)}개")
    for h in card.inf:
        print(f"   {h.code:9} {h.label:16} {h.reason[:42]}")

    print(f"\n[기한]  {len(card.tim)}개")
    for t in card.tim:
        if t.days_left is not None:
            print(f"   {t.code:9} {t.label:18} D{t.days_left:+d} ({t.severity})")
        else:
            print(f"   {t.code:9} {t.label:18} - {t.unresolved or '기한 없음'}")

    print(f"\n[다음 행동]  규칙 {card.next_action.rule_no}번 -> {card.next_action.action}")
    print(f"             {card.next_action.why}")
    print(f"             발화 코드: {', '.join(card.next_action.codes) or '(기본)'}")
    if card.also:
        print("             참고사항: " + ", ".join(f"{h.rule_no}번 {h.action}" for h in card.also))

    print("\n[절차 안내]  무엇을 / 어디에 / 어떻게 / 언제까지")
    print(f"             {card.procedure}   <- 지식베이스를 채우기 전까지 비어 있다")

    if card.checklist:
        c = card.checklist
        if c.unresolved:
            print(f"\n[제출 준비물]  {c.unresolved}")
        else:
            print(f"\n[제출 준비물]  {c.done}/{c.total}")
            for i in c.items:
                print(f"   [{i.state}] {i.label}" + (f" - {i.reason}" if i.reason else ""))
            if c.form_name:
                print(f"\n[서식]        {c.form_name}" + (f"  {c.form_url}" if c.form_url else ""))
            if c.statute:
                print(f"[근거 조문]    {c.statute}")
            if c.submit_to:
                print(f"[제출처]      {c.submit_to}")
                _print_agency(c.submit_to, result)

    print(f"\n전체 JSON 은 {len(card.model_dump_json())} 바이트입니다. 화면은 이것만 읽으면 됩니다.\n")


if __name__ == "__main__":
    main()
