"""규칙표 13줄을 규칙마다 실제 사건 자료로 발화시킨다.

규칙 단위 시험(test_rules.py)은 코드를 손으로 넣은 상태로 규칙표만 본다. 여기서는 서류를 넣은
research-engine 출력으로 **파이프라인 전체**가 그 규칙까지 가는지 본다. 사건은
``시험자료/규칙별/`` 에 있고(만들기.py 로 만든다), 여기 픽스처는 그 ``out.json`` 사본이다.

아직 그 규칙에 닿지 못하는 사건은 xfail(strict)로 둔다 — 원인을 적어 두고, 고쳐지면
XPASS 로 실패해서 표시를 떼라고 알려 준다. 원인은 시험자료/규칙별/README.md 에 있다.
"""

import json
from pathlib import Path

import pytest

from action_engine import build_card

RULES = Path(__file__).parent / "fixtures" / "rules"

# 서류가 아니라 엔진 쪽 이유로 아직 닿지 못하는 규칙. 비어 있는 것이 정상이다 —
# 새로 막히면 원인을 적어 여기에 넣는다(고쳐지면 XPASS 로 실패해서 알려 준다).
BLOCKED: dict[str, str] = {}

CASES = sorted(p.stem for p in RULES.glob("*.json"))


def _expect(name: str) -> dict:
    case = Path(__file__).resolve().parents[2] / "시험자료" / "규칙별" / name / "case.json"
    return json.loads(case.read_text(encoding="utf-8"))["expect"]


def test_규칙마다_사건이_하나씩_있다():
    assert [int(n[:2]) for n in CASES] == list(range(13))


@pytest.mark.parametrize("name", [
    pytest.param(n, marks=pytest.mark.xfail(reason=BLOCKED[n], strict=True)) if n in BLOCKED else n
    for n in CASES
])
def test_사건_자료로_그_규칙이_발화한다(name):
    card = build_card(json.loads((RULES / f"{name}.json").read_text(encoding="utf-8")))
    expect = _expect(name)
    assert card.next_action is not None
    assert (card.next_action.rule_no, card.next_action.action) == (expect["rule"], expect["action"])
