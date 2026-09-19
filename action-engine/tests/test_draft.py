"""서류 초안 조립 테스트.

여기서 고정하는 것은 '무엇을 만드는가'보다 **무엇을 만들지 않는가**다.
지어낸 문장 하나가 그대로 수사기관에 제출되는 서류에 들어간다.
"""

import copy
import json
from pathlib import Path

import pytest

from action_engine import build_card
from action_engine.draft import build_draft

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def recent() -> dict:
    return json.loads((FIXTURES / "suspension_recent.json").read_text(encoding="utf-8"))


@pytest.fixture()
def draft(recent):
    return build_draft(recent, build_card(recent))


# ── 만드는 것 ──────────────────────────────────────────────────────────


def test_초안이_만들어진다(draft):
    assert draft is not None
    assert draft.form_name == "수사중지 결정 이의제기서"


def test_사건_경위는_시간순이다(recent):
    """픽스처가 시간순으로 들어 있어도 우연히 맞은 것이 아니게, 일부러 뒤집어 넣고 본다."""
    shuffled = copy.deepcopy(recent)
    shuffled["timeline"]["events"] = list(reversed(shuffled["timeline"]["events"]))
    draft = build_draft(shuffled, build_card(shuffled))

    history = [s for s in draft.sections if s.heading == "사건 경위"][0]
    assert [line.date for line in history.lines] == [
        "2021. 5. 18.", "2021. 5. 25.", "2021. 5. 25.", "2025. 6. 3.", "2026. 8. 18.",
    ]


def test_기록에서_찾은_값은_채운다(draft):
    filled = {f.key: f for f in draft.fields}
    assert filled["case_number"].value == "2021형제45678"
    assert filled["case_number"].filled_from == "case_record"


# ── 만들지 않는 것 ─────────────────────────────────────────────────────


def test_모든_줄에_출처가_있다(draft):
    for section in draft.sections:
        for line in section.lines:
            assert line.citations, line.text
            assert all(c.doc_id for c in line.citations)


def test_출처_없는_사건은_넣지_않는다(recent):
    broken = copy.deepcopy(recent)
    broken["timeline"]["events"][0]["sources"] = []
    draft = build_draft(broken, build_card(broken))

    assert draft.dropped == 1
    history = [s for s in draft.sections if s.heading == "사건 경위"][0]
    mine = sum(1 for e in recent["timeline"]["events"] if e.get("evidence_level") == "user")  # 직접 적은 메모는 원래 빠진다
    assert len(history.lines) == len(recent["timeline"]["events"]) - 1 - mine


def test_법조문과_제출처는_지식베이스에서만_온다(draft):
    kb = {f.key: f for f in draft.fields if f.filled_from == "knowledge_base"}
    assert kb["statute"].value == "경찰수사규칙 제101조"
    assert kb["submit_to"].value.startswith("해당 사법경찰관이 소속된")


def test_지식베이스에_서식이_없으면_초안을_만들지_않는다(recent):
    """서식 이름을 지어내면 그대로 잘못된 서류를 쓰게 된다."""
    card = build_card(recent)
    assert build_draft(recent, card, action="ACT-근거보완") is None


def test_신청인_정보는_언제나_빈칸이다(draft):
    """자료에 있을 수 없는 값이다. 채우면 남의 이름이 적힌다."""
    blanks = {f.key: f for f in draft.unfilled}
    for key in ("applicant_name", "applicant_contact", "applicant_address"):
        assert key in blanks
        assert blanks[key].value is None
        assert "직접" in blanks[key].reason


def test_기록으로_확인되지_않은_값은_빈칸으로_남는다(recent):
    broken = copy.deepcopy(recent)
    for status in broken["analysis"]["slot_statuses"]:
        if status["slot"] == "case_number":
            status["state"] = "claimed_only"
    draft = build_draft(broken, build_card(broken))

    assert "case_number" not in {f.key for f in draft.fields}
    reason = {f.key: f.reason for f in draft.unfilled}["case_number"]
    assert "확인되지 않았습니다" in reason


def test_진술과_기록을_섞지_않는다(draft):
    history = [s for s in draft.sections if s.heading == "사건 경위"][0]
    levels = {line.evidence_level for line in history.lines}
    assert levels == {"record", "statement"}


def test_이의_사유는_비워_둔다(draft):
    """판단이 들어가는 칸이다. 대신 쓰지 않는다."""
    reason = [s for s in draft.sections if s.heading == "이의 사유"][0]
    assert reason.lines == []
    assert "직접 적어" in reason.note


def test_초안_표시는_떼지_않는다(draft):
    assert draft.is_draft is True


def test_적어_내는_서류가_아니면_초안을_만들지_않는다(recent):
    """서식 이름이 있어도 우리가 써 줄 수 있는 서류가 아닌 경우가 있다.

    ACT-단계확인의 '형사사법포털 사건조회'는 접속해서 조회하는 절차이지 적어 내는
    서류가 아니다. 거기에 사건 경위 초안을 내놓으면 없는 서류를 쓰려고 앉게 된다.
    """
    card = build_card(recent)
    assert build_draft(recent, card, action="ACT-단계확인") is None
    # 지식베이스에 '생성가능' 으로 적힌 서류에는 그대로 만들어진다
    assert build_draft(recent, card, action="ACT-이의제기-수사중지") is not None


def test_요청하는_서류는_이의_사유가_아니라_요청_사항을_비워_둔다(recent):
    """자료·의견 제출서(수사준칙 제25조)는 결정에 불복하는 서류가 아니다. '이의 사유' 칸을 달면 잘못 쓰게 된다."""
    card = build_card(recent)
    for action in ("ACT-신규정보제출", "ACT-모순확인", "ACT-공소시효", "ACT-증거보존"):
        d = build_draft(recent, card, action=action)
        assert d is not None, action
        headings = [s.heading for s in d.sections]
        assert "요청 사항" in headings and "이의 사유" not in headings, action
        ask = [s for s in d.sections if s.heading == "요청 사항"][0]
        assert ask.lines == [] and "직접 적어" in ask.note, action
