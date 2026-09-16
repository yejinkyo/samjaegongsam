"""무엇을 언제 내고 어떤 답을 받았는가 — 제출·회신 기록 테스트.

`suspension_recent` 는 기한이 살아 있는(D-5) 수사중지 사건이라 '낸다'는 행동이
실제로 다음 행동에 올라와 있다. 낸 뒤 화면이 어떻게 달라져야 하는지를 여기서 고정한다.
"""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from action_engine import INF, Submission, SubmissionResponse, build_card, status_of, waiting_days
from action_engine.submissions import ANSWERED, SUBMITTED

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def recent() -> dict:
    """고소 → 수사중지, 이의제기 기한이 아직 남아 있는 사건."""
    return json.loads((FIXTURES / "suspension_recent.json").read_text(encoding="utf-8"))


def _sub(action: str, day: date, *, receipt: str | None = None, response=None) -> Submission:
    return Submission(submission_id="s1", action=action, submitted_at=day,
                      evidence_doc_id=receipt, response=response)


# ── 낸 것은 다음 행동에서 내린다 ────────────────────────────────────────


def test_기록이_없으면_카드는_지금까지와_같다(recent):
    assert build_card(recent).model_dump() == build_card(recent, []).model_dump()


def test_이미_낸_행동은_다음_행동이_아니다(recent):
    before = build_card(recent)
    assert before.next_action.action == "ACT-불복기한"   # 이 사건의 기한 행동

    after = build_card(recent, [_sub("ACT-불복기한", date(2026, 9, 10))])
    assert after.next_action.action != "ACT-불복기한"
    assert after.next_action.action == before.also[0].action   # 다음 순위가 올라온다


def test_낸_행동은_참고사항에_남는다(recent):
    """다음 행동에서 내리되 없애지는 않는다 — 없애면 무엇을 냈는지가 화면에서 사라진다."""
    after = build_card(recent, [_sub("ACT-불복기한", date(2026, 9, 10))])
    assert after.also[0].action == "ACT-불복기한"


def test_낸_기록은_카드에_그대로_실린다(recent):
    sub = _sub("ACT-불복기한", date(2026, 9, 10))
    after = build_card(recent, [sub])
    assert [s.submission_id for s in after.submissions] == ["s1"]
    assert after.submissions[0].submitted_at == date(2026, 9, 10)


# ── 접수증이 없으면 본인 말뿐이다 ───────────────────────────────────────


def test_접수증_없는_제출은_출처누락으로_남는다(recent):
    after = build_card(recent, [_sub("ACT-불복기한", date(2026, 9, 10))])
    hits = [h for h in after.inf if h.code == INF.SOURCE_MISSING and "접수증" in h.reason]
    assert len(hits) == 1
    assert hits[0].confidence == "추정"   # 냈다는 것 자체가 사용자의 말이다


def test_접수증이_있으면_출처누락을_붙이지_않는다(recent):
    after = build_card(recent, [_sub("ACT-불복기한", date(2026, 9, 10), receipt="doc-접수증")])
    assert not [h for h in after.inf if h.code == INF.SOURCE_MISSING and "접수증" in h.reason]


# ── 답을 기다리는 날수 ─────────────────────────────────────────────────


def test_답이_없으면_기다린_날수를_센다(recent):
    """기준일(as_of)은 픽스처가 정한다. 날수는 낸 날부터 그 기준일까지다."""
    as_of = date.fromisoformat(recent["as_of"])
    submitted = as_of - timedelta(days=12)
    after = build_card(recent, [_sub("ACT-불복기한", submitted)])
    hits = [h for h in after.inf if h.code == INF.RECORD_UNCHECKED and "회신 자료가 없습니다" in h.reason]
    assert len(hits) == 1
    assert "12일째" in hits[0].reason


def test_회신이_오면_날수를_세지_않는다(recent):
    answered = _sub("ACT-불복기한", date(2026, 9, 10),
                    response=SubmissionResponse(received_at=date(2026, 9, 14)))
    after = build_card(recent, [answered])
    assert not [h for h in after.inf if h.code == INF.RECORD_UNCHECKED and "회신 자료가 없습니다" in h.reason]


def test_낸_당일에는_날수를_붙이지_않는다():
    sub = _sub("ACT-불복기한", date(2026, 9, 15))
    assert waiting_days(sub, date(2026, 9, 15)) == 0


def test_기다린_날수는_뺄셈_그대로다():
    sub = _sub("ACT-불복기한", date(2026, 9, 1))
    assert waiting_days(sub, date(2026, 9, 13)) == 12


def test_회신이_오면_기다린_날수는_없다():
    sub = _sub("ACT-불복기한", date(2026, 9, 1),
               response=SubmissionResponse(received_at=date(2026, 9, 5)))
    assert waiting_days(sub, date(2026, 9, 13)) is None


def test_상태는_회신_여부로만_갈린다():
    day = date(2026, 9, 1)
    assert status_of(_sub("ACT-불복기한", day)) == SUBMITTED
    assert status_of(_sub("ACT-불복기한", day, response=SubmissionResponse(received_at=day))) == ANSWERED
