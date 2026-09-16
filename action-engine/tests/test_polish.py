"""사건 경위 다듬기 테스트.

모델을 부르지 않는다. 가짜 어댑터로 '모델이 이렇게 답했을 때 우리가 무엇을 하는가'만 본다.
검사(:func:`verify`)가 이 기능의 본체다 — 통과시키는 것보다 **버리는 것**을 고정한다.
"""

import json
from pathlib import Path

import pytest

from action_engine import build_card
from action_engine.draft import build_draft
from action_engine.polish import polish, verify

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def draft():
    result = json.loads((FIXTURES / "suspension_recent.json").read_text(encoding="utf-8"))
    return build_draft(result, build_card(result))


@pytest.fixture()
def lines(draft):
    return [s for s in draft.sections if s.heading == "사건 경위"][0].lines


class Fake:
    """정해 둔 글을 돌려주는 어댑터."""

    def __init__(self, text: str):
        self.text = text
        self.prompt: str | None = None

    def complete(self, prompt: str) -> str:
        self.prompt = prompt
        return self.text


class Broken:
    def complete(self, prompt: str) -> str:
        raise TimeoutError("응답 없음")


GOOD = (
    "고소인은 2021. 5. 18. 18,000,000원의 피해를 입었다고 진술하였습니다. "
    "2021. 5. 25. ○○경찰서에 고소하였다고 진술하였으며, 같은 날 접수증이 발급되었습니다. "
    "2025. 6. 3. 목격하였다는 진술이 있었고, 2026. 8. 18. 수사결과 통지서가 작성되었습니다."
)


# ── 모델이 없을 때 ─────────────────────────────────────────────────────


def test_모델이_없으면_골격을_쓴다(draft):
    """키가 없는 것은 오류가 아니다. 조용히 골격으로 돌아간다."""
    out = polish(draft, client=None)
    assert out.text is None
    assert out.used_model is False
    assert "모델을 쓸 수 없습니다" in out.rejected


def test_호출이_실패해도_골격을_쓴다(draft):
    out = polish(draft, client=Broken())
    assert out.text is None
    assert "TimeoutError" in out.rejected


# ── 잘 답했을 때 ───────────────────────────────────────────────────────


def test_검사를_통과하면_쓴다(draft):
    out = polish(draft, client=Fake(GOOD))
    assert out.used_model is True
    assert out.text.startswith("고소인은")
    assert out.rejected is None


def test_법조문과_제출처는_모델에게_주지_않는다(draft):
    """줄 필요가 없고, 주면 바꿔 쓸 수 있다."""
    fake = Fake(GOOD)
    polish(draft, client=fake)
    assert "경찰수사규칙" not in fake.prompt
    assert "상급경찰관서" not in fake.prompt
    assert "이의제기서" not in fake.prompt


def test_진술과_기록_표시를_같이_준다(draft):
    fake = Fake(GOOD)
    polish(draft, client=fake)
    assert "[진술]" in fake.prompt and "[기록]" in fake.prompt


# ── 버리는 것 ─────────────────────────────────────────────────────────


def test_없던_숫자가_생기면_버린다(draft):
    bad = GOOD + " 2024. 1. 1. 추가 조사가 있었습니다."
    out = polish(draft, client=Fake(bad))
    assert out.text is None
    assert "자료에 없는 숫자" in out.rejected


def test_금액을_바꾸면_버린다(lines):
    bad = "고소인은 2021. 5. 18. 19,000,000원의 피해를 입었다고 진술하였습니다."
    assert "자료에 없는 숫자" in verify(lines, bad)


def test_자릿점은_숫자를_바꾸지_않는다(lines):
    """1,800만과 18000000 은 같은 숫자다 — 표기 때문에 버리면 안 된다."""
    ok = "고소인은 2021. 5. 18. 18000000원의 피해를 입었다고 진술하였습니다."
    assert verify(lines, ok) is None


def test_평가하는_말이_들어가면_버린다(draft):
    bad = GOOD + " 이 결정은 부당합니다."
    out = polish(draft, client=Fake(bad))
    assert out.text is None
    assert "평가하는 말" in out.rejected


@pytest.mark.parametrize("word", ["위법", "명백", "억울", "보입니다", "판단됩니다"])
def test_판단하는_표현은_전부_버린다(lines, word):
    assert "평가하는 말" in verify(lines, GOOD + f" 이는 {word}.")


def test_진술을_단정형으로_바꾸면_버린다(lines):
    """'진술하였습니다'가 사라지면 사람의 말이 기록처럼 읽힌다."""
    bad = "2021. 5. 18. 18,000,000원의 피해가 발생하였습니다. 2021. 5. 25. 고소하였습니다."
    assert "단정해서" in verify(lines, bad)


def test_빈_글은_버린다(lines):
    assert verify(lines, "   ") == "빈 글이 돌아왔습니다"


def test_지나치게_길어지면_버린다(lines):
    padded = GOOD + " 같은 날 접수증이 발급되었습니다." * 60
    assert "지나치게" in verify(lines, padded)
