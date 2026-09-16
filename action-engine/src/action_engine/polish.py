"""초안의 사건 경위를 읽을 수 있는 문장으로 엮는다 (선택 · 모델을 쓴다).

:mod:`draft` 가 만든 골격이 먼저고 이건 그 위에 얹는 층이다. **없으면 없는 대로 돌아간다** —
키가 없거나, 호출이 실패하거나, 돌려받은 글이 검사를 통과하지 못하면 골격을 그대로 쓴다.
발표 중에 모델이 죽어도 화면이 빈칸이 되면 안 된다.

모델에게 맡기는 일은 **줄을 문장으로 잇는 것 하나**뿐이다.

- 법조문·기한·제출처·서식명은 아예 주지 않는다. 줄 필요가 없고, 주면 바꿔 쓸 수 있다.
- 돌려받은 글은 검사를 통과해야 쓴다. **입력에 없던 숫자가 하나라도 생기면 버린다** —
  날짜 하나, 금액 한 자리가 틀리면 그대로 수사기관에 내는 서류에 들어간다.
- 평가하는 말이 들어가도 버린다. 사실과 날짜만 적는 자리다.
- 진술에서 온 줄은 '진술하였습니다'로 남아야 한다. 기록처럼 단정해서 쓰면 안 된다.

검사에 걸리면 조용히 골격으로 떨어지고, 왜 걸렸는지는 ``rejected`` 에 남는다.
"""

from __future__ import annotations

import os
import re
from typing import Protocol

from pydantic import BaseModel, Field

from .schema import DraftDocument, DraftLine

MODEL = "claude-sonnet-5"

# 평가·판단이 들어간 말. 하나라도 있으면 버린다.
BANNED_WORDS = (
    "부당", "위법", "명백", "틀림없", "억울", "잘못", "과실", "책임",
    "의심", "확실", "분명", "당연", "마땅", "정황상", "보입니다", "보인다",
    "생각됩니다", "판단됩니다", "사료됩니다", "추정됩니다",
)

PROMPT = """아래는 한 사건의 기록에서 뽑은 줄들이다. 날짜순으로 이미 정렬되어 있다.
이것을 읽기 쉬운 경위 문단으로 이어 써라.

지켜야 할 것:
- 아래 줄에 없는 사실을 절대 덧붙이지 마라. 날짜, 금액, 이름, 장소를 새로 만들지 마라.
- 아래에 있는 숫자만 쓸 수 있다. 숫자를 바꾸거나 반올림하지 마라.
- [진술] 로 표시된 줄은 "~라고 진술하였습니다" 형태로만 써라. 단정해서 쓰지 마라.
- [기록] 로 표시된 줄만 단정형으로 쓸 수 있다.
- 평가하거나 판단하지 마라. "부당하다", "명백하다", "~로 보인다" 같은 말을 쓰지 마라.
- 법조문, 기한, 제출처, 서류 이름을 쓰지 마라. 그건 여기서 다루지 않는다.
- 문단만 출력해라. 제목이나 설명을 붙이지 마라.

줄:
{lines}"""


class Client(Protocol):
    """모델 어댑터. 프롬프트 하나를 받아 글 하나를 돌려준다."""

    def complete(self, prompt: str) -> str: ...


class PolishResult(BaseModel):
    """다듬기 결과. ``text`` 가 None 이면 골격을 그대로 쓰라는 뜻이다."""

    text: str | None = None
    used_model: bool = False
    rejected: str | None = Field(default=None, description="검사에 걸린 이유. 걸렸을 때만 찬다")


def _numbers(text: str) -> set[str]:
    """글에 나오는 숫자 덩어리. 자릿점은 떼고 본다 — 1,800만과 1800만은 같은 숫자다."""
    return {n for n in re.findall(r"\d+", text.replace(",", "")) if n}


def _lines_for_prompt(lines: list[DraftLine]) -> str:
    out = []
    for line in lines:
        mark = "[진술]" if line.evidence_level == "statement" else "[기록]"
        out.append(f"- {line.date or '날짜 모름'} {mark} {line.text}")
    return "\n".join(out)


def verify(lines: list[DraftLine], text: str) -> str | None:
    """돌려받은 글을 검사한다. 통과하면 None, 걸리면 이유."""
    text = (text or "").strip()
    if not text:
        return "빈 글이 돌아왔습니다"

    source = " ".join((line.date or "") + " " + line.text for line in lines)

    invented = _numbers(text) - _numbers(source)
    if invented:
        return f"자료에 없는 숫자가 들어 있습니다: {', '.join(sorted(invented))}"

    found = [w for w in BANNED_WORDS if w in text]
    if found:
        return f"평가하는 말이 들어 있습니다: {', '.join(found)}"

    # 진술에서 온 줄이 있으면 그 표시가 남아 있어야 한다
    if any(line.evidence_level == "statement" for line in lines) and "진술" not in text:
        return "진술에서 온 내용을 기록처럼 단정해서 썼습니다"

    if len(text) > max(len(source) * 3, 400):
        return "원래 줄보다 지나치게 길어졌습니다 — 없던 내용이 붙었을 수 있습니다"

    return None


def anthropic_client(model: str = MODEL) -> Client | None:
    """키와 SDK 가 다 있을 때만 어댑터를 만든다. 없으면 None — 골격으로 돈다."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        return None

    class _Adapter:
        def __init__(self) -> None:
            self._client = anthropic.Anthropic()

        def complete(self, prompt: str) -> str:
            message = self._client.messages.create(
                model=model,
                max_tokens=1200,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in message.content if block.type == "text")

    return _Adapter()


def polish(draft: DraftDocument, client: Client | None = None) -> PolishResult:
    """사건 경위를 문장으로 엮는다. 못 하면 골격을 그대로 쓰라고 돌려준다."""
    history = [s for s in draft.sections if s.heading == "사건 경위"]
    lines = history[0].lines if history else []
    if not lines:
        return PolishResult(rejected="엮을 줄이 없습니다")

    client = client or anthropic_client()
    if client is None:
        return PolishResult(rejected="모델을 쓸 수 없습니다 (키 또는 SDK 없음)")

    try:
        text = client.complete(PROMPT.format(lines=_lines_for_prompt(lines)))
    except Exception as exc:  # noqa: BLE001 — 어떤 실패든 골격으로 떨어진다
        return PolishResult(rejected=f"호출에 실패했습니다: {type(exc).__name__}")

    reason = verify(lines, text)
    if reason:
        return PolishResult(rejected=reason)

    return PolishResult(text=text.strip(), used_model=True)
