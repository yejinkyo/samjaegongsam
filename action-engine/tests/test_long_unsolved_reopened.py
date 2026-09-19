"""재수사로 죄명이 바뀐 장기 미제 사건 — 공소시효는 가장 최근 통지서의 죄명으로 계산한다.

research-engine 의 long_unsolved_reopened 픽스처 출력을 그대로 받는다(인물·사건은 가상).
"""

from action_engine import build_card
from action_engine.codes import TIM


def test_바뀐_죄명으로_공소시효를_판단한다(reopened):
    """2008 통지서의 '미성년자 약취·유인'(구법 7년)으로 계산하면 2013년에 끝난 사건이 된다.

    지금 죄명은 2022 통지서의 '살인'이다. 2006년 범행이라 종전 시효 15년이 2015-07-31 에 남아 있어
    공소시효 배제(형사소송법 제253조의2)가 적용된다.
    """
    limitation = {t.code: t for t in build_card(reopened).tim}[TIM.STATUTE_LIMITATION]
    assert limitation.unresolved is None
    assert "살인" in limitation.advisory and "폐지가 적용됩니다" in limitation.advisory
    assert limitation.due_date is None  # 만료일이 없다
