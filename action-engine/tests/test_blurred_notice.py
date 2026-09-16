"""결정 내용을 읽을 수 없는 통지서 — 모를 때 모른다고 말하는지.

비에 젖어 결정 부분만 번진 통지서다. 단계는 '결과'까지 왔는데 무슨 결정인지 알 수 없다.
이때 아무 단계나 찍으면 그 뒤 판단이 전부 그 위에 쌓인다.
입력 자료는 시험자료/흐린-통지서/ 에 있다.
"""

import json
from pathlib import Path

import pytest

from action_engine import ST, Confidence, build_card
from action_engine.draft import build_draft

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def blurred() -> dict:
    return json.loads((FIXTURES / "blurred_notice.json").read_text(encoding="utf-8"))


@pytest.fixture()
def card(blurred):
    return build_card(blurred)


def test_읽히지_않으면_단계를_찍지_않는다(card):
    assert card.st.code == ST.UNKNOWN
    assert card.st.confidence == Confidence.UNDETERMINED
    assert "찾지 못했습니다" in card.st.reason


def test_단계부터_확인하라고_안내한다(card):
    assert card.next_action.action == "ACT-단계확인"


def test_조회_절차에는_초안을_만들지_않는다(blurred, card):
    """'형사사법포털 사건조회'는 접속해서 조회하는 절차이지 적어 내는 서류가 아니다."""
    assert card.checklist.form_name == "형사사법포털 사건조회 (온라인)"
    assert build_draft(blurred, card) is None


def test_읽히지_않은_줄은_되물을_거리로_남는다(blurred):
    pending = [q for q in blurred["clarifications"] if q["status"] == "pending"]
    assert any(q["doc_id"] == "blurred_notice_2024" for q in pending)
