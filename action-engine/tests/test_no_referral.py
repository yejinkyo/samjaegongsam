"""불송치 사건 — 통지를 받고 가장 먼저 열리는 길이 안내되는지.

시험용 사건 자료를 만들어 돌려 보다가 두 가지가 드러나 픽스처로 굳혔다.
둘 다 '엉뚱한 곳에 엉뚱한 서류를 내게 만드는' 종류의 오류였다.
입력 자료는 시험자료/불송치-이의신청/ 에 있다.
"""

import json
from pathlib import Path

import pytest

from action_engine import ST, build_card
from action_engine.draft import build_draft

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def no_referral() -> dict:
    """2024 고소 → 2026. 8. 25. 불송치(혐의없음) → 통지 뒤 계좌 거래내역 확보."""
    return json.loads((FIXTURES / "no_referral.json").read_text(encoding="utf-8"))


@pytest.fixture()
def card(no_referral):
    return build_card(no_referral)


def test_불송치는_경찰_불송치로_판정한다(card):
    """통지서에 '불송치(혐의없음)' 으로 적혀 온다.

    '혐의없음'은 불송치의 이유이지 검찰의 불기소 처분이 아니다. 검찰 불기소(ST-302)로
    보면 경찰에 낼 이의신청 대신 검찰 항고를 안내하게 된다 — 제출처도 서식도 전부 달라진다.
    """
    assert card.st.code == ST.POLICE_NO_REFERRAL


def test_기한이_없어도_불복_경로를_안내한다(card):
    """불송치 이의신청(형사소송법 제245조의7)은 법정 기한이 없다.

    기한이 급할 때만 발화하는 규칙으로는 영영 안내되지 않았다 — 급해질 수가 없어서다.
    """
    assert card.next_action.action == "ACT-불복기한"


def test_기한이_없다는_것과_못_구한_것을_구별한다(card):
    """'기한 없음'은 그 자체로 필요한 정보다. '아직 못 채웠다'와 섞으면 안 된다."""
    tim = {t.code: t for t in card.tim}
    assert tim["TIM-011"].severity == "ok"
    assert tim["TIM-011"].due_date is None
    assert tim["TIM-011"].unresolved is None
    assert tim["TIM-011"].advisory


def test_불송치에_맞는_서식과_제출처가_나온다(card):
    c = card.checklist
    assert c.form_name == "불송치 결정 이의신청서"
    assert c.form_source == "경찰수사규칙 별지 제125호 서식"
    assert c.submit_to == "불송치 결정을 한 사법경찰관의 소속 관서의 장"
    assert c.statute == "형사소송법 제245조의7"


def test_초안도_그_서식으로_만들어진다(no_referral, card):
    draft = build_draft(no_referral, card)
    assert draft.form_name == "불송치 결정 이의신청서"
    history = [s for s in draft.sections if s.heading == "사건 경위"][0]
    assert history.lines and all(line.citations for line in history.lines)
