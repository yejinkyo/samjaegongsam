from pathlib import Path

import pytest

from research_engine.pipeline import ResearchPipeline, load_case

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fraud_case():
    return load_case(FIXTURES / "used_goods_fraud" / "case.json")


@pytest.fixture(scope="session")
def fraud_result(fraud_case):
    return ResearchPipeline().run(fraud_case)
