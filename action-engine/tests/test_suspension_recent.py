"""기한이 살아 있는 수사중지 사건 — 지식베이스가 실제로 쓰이는 경로.

기존 픽스처는 전부 결정 후 몇 년이 지나 불복 기한이 만료다. 만료된 기한은 행동에서
빼기로 했으므로(rules.json 의 expired_note) 규칙 2번이 한 번도 켜지지 않았고,
그 결과 서식·제출처·조문이 화면에 나온 적이 없었다.

이 픽스처는 결정 통지 25일째(기한 30일 중 5일 남음)를 본다. 여기서만 확인되는 것:

    규칙 2번 -> ACT-불복기한 -> by_stage[ST-201] -> ACT-이의제기-수사중지

ST 로 한 번 더 갈라 조회하는 단계가 실제로 동작하는지도 여기서 잠근다.
"""

import json
from pathlib import Path

import pytest

from action_engine import build_card
from action_engine.agencies import describe_submit_to
from action_engine.schema import Confidence

FIXTURE = Path(__file__).parent / "fixtures" / "suspension_recent.json"


@pytest.fixture(scope="module")
def card():
    return build_card(json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_수사중지_피의자중지로_판정한다(card):
    assert card.st.code == "ST-201"
    assert card.st.confidence is Confidence.CONFIRMED


def test_이의제기_기한이_임박으로_남아_있다(card):
    tim = {d.code: d for d in card.tim}
    assert tim["TIM-014"].severity == "critical"
    assert tim["TIM-014"].days_left == 5


def test_기한이_살아_있으면_불복이_다음_행동이다(card):
    assert card.next_action.rule_no == 2
    assert card.next_action.action == "ACT-불복기한"
    assert "TIM-014" in card.next_action.codes


def test_ST로_갈라_수사중지_이의제기_서류를_찾는다(card):
    c = card.checklist
    assert c.action == "ACT-이의제기-수사중지"
    assert c.form_name == "수사중지 결정 이의제기서"
    assert c.statute == "경찰수사규칙 제101조"
    assert c.total == 2


def test_이미_가진_통지서는_보유로_대조된다(card):
    states = {i.label: i.state for i in card.checklist.items}
    assert states["수사중지 결정 통지서"] == "보유"
    assert states["수사중지 결정 이의제기서"] == "생성가능"


def test_상급경찰관서를_실제_기관명으로_바꾼다(card):
    found = describe_submit_to(card.checklist.submit_to, "대구성서경찰서")
    assert found["resolved"] is True
    assert found["target"]["name"] == "대구광역시경찰청"


def test_수집되지_않은_지역은_지어내지_않는다(card):
    found = describe_submit_to(card.checklist.submit_to, "서울강남경찰서")
    assert found["resolved"] is False
    assert "기관 자료에 없습니다" in found["reason"]
