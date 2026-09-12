"""발표용 데모 — 터미널에서 그대로 돌린다.

    cd action-engine
    uv run python examples/demo.py          # 전체
    uv run python examples/demo.py 2        # 한 장면만

심사위원이 반드시 묻는 질문은 하나다 — "법률 분야인데 AI가 틀리면 어떻게 하죠?"
네 장면이 그 질문에 차례로 답한다.

    1  같은 엔진이 사건마다 다른 결론을 내고, 왜 그런지 규칙 번호로 말한다
    2  하루 차이로 시효가 5년 갈리는 것을 잡는다
    3  모르는 것은 모른다고 하고 지어내지 않는다
    4  틀리면 어디가 틀렸는지 짚을 수 있다
"""

import json
import sys
from datetime import date
from pathlib import Path

from action_engine import (
    ST,
    CaseState,
    CodeHit,
    build_card,
    build_checklist,
    compute_deadlines,
    compute_limitation,
    decide,
    describe_submit_to,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"
W = 64


def rule(ch: str = "-") -> None:
    print(ch * W)


def title(n: int, text: str, claim: str) -> None:
    print(f"\n{'=' * W}\n  장면 {n}.  {text}\n  {claim}\n{'=' * W}")


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def state_of(st: str, as_of: date = date(2026, 9, 12)) -> CaseState:
    return CaseState(case_id="demo", case_type="demo", as_of=as_of,
                     st=CodeHit(code=st, label=st, reason="데모"), inf=[], tim=[])


# ── 1 ───────────────────────────────────────────────────────────────────


def scene_1() -> None:
    title(1, "같은 엔진, 다른 결론", "규칙 하나가 모든 사건에 같은 답을 내지 않습니다")

    for name, label in [("long_unsolved_missing", "장기 미제 실종 (2015 실종 → 2022 수사중지)"),
                        ("investigation_suspended", "수사중지 (2021 고소 → 2023 참고인중지 → 2025 제보)"),
                        ("used_goods_fraud", "중고거래 사기 (2026 송금 → 연락두절)")]:
        card = build_card(load(name))
        print(f"\n  {label}")
        print(f"    단계    {card.st.code} {card.st.label} ({card.st.confidence})")
        print(f"    상태    {', '.join(h.code for h in card.inf)}")
        print(f"    행동    규칙 {card.next_action.rule_no}번 · {card.next_action.action}")
        print(f"    근거    {card.next_action.why}")
        print(f"            발화 코드 {', '.join(card.next_action.codes) or '(기본)'}")

    rule()
    print("  같은 사건이라도 시간이 흐르면 조언이 바뀝니다.")
    print("  수사중지 결정 통지를 받고 며칠 지났는지만 다릅니다.\n")

    for days, when in [(3, "통지 3일 뒤"), (25, "통지 25일 뒤"), (1200, "통지 3년 뒤")]:
        s = state_of(ST.SUSPENDED_WITNESS)
        s.inf = [CodeHit(code="INF-011", label="신규 인적 진술", reason="2025 목격 제보")]
        basis = date.fromordinal(date(2026, 9, 12).toordinal() - days)
        s.tim = compute_deadlines(s, {"decision_time": basis})
        d = decide(s)
        t = next(x for x in s.tim if x.code == "TIM-014")
        left = f"D{t.days_left:+d}" if t.days_left is not None else "-"
        print(f"    {when:12} 이의제기 기한 {left:>6} ({t.severity:7})  →  규칙 {d.main.rule_no}번 {d.main.action}")

    print("\n  기한이 살아 있으면 그것부터, 지나면 남은 경로로 옮겨 갑니다.")
    print("  가중치도 점수도 없습니다. 규칙 10줄을 순서대로 훑을 뿐입니다.")
    print("  경우의 수는 1,572,864개(ST 12 × INF 2¹⁰ × TIM 2⁷)이고,")
    print("  그것을 나열하는 대신 '무엇이 더 급한가'를 열 줄로 선언했습니다.")


# ── 2 ───────────────────────────────────────────────────────────────────


def scene_2() -> None:
    title(2, "하루가 5년을 가릅니다", "장기·미제 사건에서 가장 자주 나오는 오답입니다")

    print("\n  같은 죄명, 같은 계산기. 범행일만 하루 다릅니다.\n")
    results = []
    for d in (date(2007, 12, 21), date(2007, 12, 22)):
        r = compute_limitation("강도치사", d, date(2026, 9, 12))
        results.append(r)
        print(f"    {d} 발생  →  공소시효 {r['years']:2d}년  →  {r['due_date']} 만료")
        print(f"                   {r['version_note']}")

    gap = (results[1]["due_date"] - results[0]["due_date"]).days
    print(f"\n    하루 차이인데 만료일이 {gap}일 — 약 {gap // 365}년 벌어집니다.")

    print("\n  2020년에 이 사건을 들고 왔다면 결론이 정반대였습니다.\n")
    for r in results:
        alive = r["due_date"] > date(2020, 1, 1)
        print(f"    {r['incident_end']} 발생  →  {'아직 살아 있음 (고소 가능)' if alive else '이미 끝남 (고소 불가)'}")

    rule()
    print("  2007-12-21 개정으로 기간이 늘었고, 부칙에 따라 그 전 범행은 구법입니다.")
    print("  장기·미제 사건은 대부분 개정 전이라, 신법으로 계산하면")
    print("  이미 끝난 사건을 '아직 남았다'고 안내하게 됩니다.")

    print("\n  살인은 또 다릅니다.\n")
    r = compute_limitation("살인", date(1998, 5, 1), date(2026, 9, 12))
    print(f"    1998-05-01 살인  →  {r['basis']}")
    print(f"                     {r['note']}")
    print("\n  '폐지됐으니 무조건 살아 있다'고 말하지 않습니다.")


# ── 3 ───────────────────────────────────────────────────────────────────


def scene_3() -> None:
    title(3, "모르는 것은 모른다고 합니다", "빈칸을 지어내지 않는 것이 이 제품의 안전장치입니다")

    print("\n  ① 죄명을 모르면 시효를 계산하지 않습니다")
    r = compute_limitation(None, date(2010, 1, 1), date(2026, 9, 12))
    print(f"     → {r['reason']}")
    r = compute_limitation("상해치상", date(2010, 1, 1), date(2026, 9, 12))
    print(f"     → {r['reason']}")
    print("       비슷한 죄명으로 대신 계산하지 않습니다. 한 구간만 달라도 5년이 차이 납니다.")

    print("\n  ② 자료를 모은 지역 밖이면 제출처를 지어내지 않습니다")
    for station in ("대구수성", "서울강남"):
        r = describe_submit_to("해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장", station)
        if r["resolved"]:
            print(f"     {station}  →  {r['target']['name']}")
            print(f"                {r['hint']}")
        else:
            print(f"     {station}  →  {r['reason']}")

    print("\n  ③ 이미 지난 기한은 '다음 행동'으로 올리지 않습니다")
    s = state_of(ST.SUSPENDED_SUSPECT)
    s.tim = compute_deadlines(s, {"decision_time": date(2022, 3, 15)})
    t = next(x for x in s.tim if x.code == "TIM-014")
    print(f"     수사중지 이의제기 기한 30일 · 2022-03-15 결정  →  {t.severity}")
    print("     닫힌 경로를 '지금 하세요'라고 안내하면 안 됩니다. 만료 사실만 남깁니다.")

    print("\n  ④ 검증된 절차가 없으면 문구를 만들지 않습니다")
    c = build_checklist("ACT-근거보완", [])
    print(f"     → {c.unresolved}")
    print("       무엇을·어디에·어떻게·언제까지는 검증된 지식베이스에서만 옵니다.")


# ── 4 ───────────────────────────────────────────────────────────────────


def scene_4() -> None:
    title(4, "틀리면 어디가 틀렸는지 짚을 수 있습니다", "가중치는 그럴 수 없습니다")

    card = build_card(load("investigation_suspended"))
    print(f"\n  결론:  규칙 {card.next_action.rule_no}번 · {card.next_action.action}\n")
    rule()
    print("  이 결론이 나온 경로를 전부 되짚습니다\n")
    print(f"    단계 판정   {card.st.code}  ({card.st.confidence})")
    print(f"                {card.st.reason}")
    print(f"                근거 문서 {', '.join(card.st.source_doc_ids)}")
    print("\n    상태 판정")
    for h in card.inf:
        src = h.source_trigger_keys[0] if h.source_trigger_keys else "자료 종류 규칙"
        print(f"      {h.code:9} {h.reason[:38]}")
        print(f"      {'':9} ← {src}")
    print(f"\n    규칙 발화   {card.next_action.rule_no}번  {card.next_action.condition}")
    print(f"                {card.next_action.why}")
    if card.also:
        print(f"    참고사항    {', '.join(f'{h.rule_no}번 {h.action}' for h in card.also)}")

    print("\n    기한")
    for t in card.tim:
        if t.days_left is not None:
            print(f"      {t.code}  D{t.days_left:+d} ({t.severity})  {t.statute or ''}")
        elif t.advisory:
            print(f"      {t.code}  {t.advisory[:46]}")
        else:
            print(f"      {t.code}  {t.unresolved}")

    rule()
    print("  '왜 0.7인가요?'에는 답할 수 없지만")
    print("  '왜 5번 규칙인가요?'에는 답할 수 있습니다.")


# ── 마무리 ──────────────────────────────────────────────────────────────


def closing() -> None:
    print(f"\n{'=' * W}")
    print("  AI가 판단하지 않습니다.")
    print("  AI는 읽고, 표가 판단하고, AI가 설명합니다.")
    print(f"{'=' * W}")
    print("\n  판정 규칙 10줄과 법령 사전은 모두 데이터 파일입니다.")
    print("  변호사가 코드를 몰라도 표를 직접 읽고 고칠 수 있습니다.")
    print("  지금 상태는 draft_unverified — 법령 원문에서 확인했지만")
    print("  법률 전문가 검수는 아직 받지 않았습니다.\n")


SCENES = {1: scene_1, 2: scene_2, 3: scene_3, 4: scene_4}


def main() -> None:
    if len(sys.argv) > 1:
        for n in sys.argv[1:]:
            SCENES[int(n)]()
        return
    for scene in SCENES.values():
        scene()
    closing()


if __name__ == "__main__":
    main()
