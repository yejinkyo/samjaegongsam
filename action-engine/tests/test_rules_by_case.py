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

# 서류가 아니라 엔진 쪽 이유로 아직 닿지 못하는 규칙
BLOCKED = {
    "00-재판단계": "research-engine 이 '구공판(공소제기)' 를 결정 내용으로 읽지 못해 단계 미확정(ST-UNKNOWN)이 된다",
    "10-공백보완": "research-engine 에 감정서 문서 종류가 없어 INF-043(전문 분석 미실시)이 늘 켜지고 9번이 먼저 발화한다",
    "11-진행확인": "INF-043 이 늘 켜지고, 수사 중인 사건은 아직 없는 '결정 내용'을 빠진 항목(INF-041)으로 센다",
    "12-상시": "INF-043 이 늘 켜져 9번이 먼저 발화한다",
}

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
