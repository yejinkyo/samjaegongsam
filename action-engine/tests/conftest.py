"""research-engine 실제 출력을 픽스처로 쓴다.

파이프라인을 여기서 돌리지 않고 저장된 JSON을 읽는다. 두 패키지가 서로를 import 하지
않아야 각자 따로 테스트할 수 있기 때문이다. 픽스처를 다시 만들려면:

    cd research-engine
    uv run research-engine run tests/fixtures/long_unsolved_missing/case.json \
        --out ../action-engine/tests/fixtures/long_unsolved_missing.json
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def missing() -> dict:
    """장기 미제 실종 — 2015 실종 → 2022 수사중지 → 2023 진정."""
    return _load("long_unsolved_missing.json")


@pytest.fixture(scope="session")
def fraud() -> dict:
    """중고거래 사기 — 송금 후 연락 두절, 신고 접수까지."""
    return _load("used_goods_fraud.json")
