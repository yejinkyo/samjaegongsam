from datetime import date, datetime

import pytest

from research_engine.extract.temporal import Anchor, TemporalNormalizer
from research_engine.schema import TimeGranularity, TimeKind

N = TemporalNormalizer(today=date(2026, 9, 11))
DOC = Anchor(date(2026, 6, 4), "document_date")


def one(text, anchor=DOC, anaphoric=None):
    matches = N.extract(text, anchor, anaphoric)
    assert len(matches) == 1, [(m.value.raw, m.value.kind) for m in matches]
    return matches[0].value


@pytest.mark.parametrize(
    "text,start",
    [
        ("2026년 6월 1일", datetime(2026, 6, 1)),
        ("2026.6.1.", datetime(2026, 6, 1)),
        ("2026-06-01", datetime(2026, 6, 1)),
        ("'23.03.05", datetime(2023, 3, 5)),
        ("23.03.05", datetime(2023, 3, 5)),
        ("단기 4290년 3월 5일", datetime(1957, 3, 5)),
    ],
)
def test_absolute_dates(text, start):
    v = one(text)
    assert v.kind is TimeKind.ABSOLUTE
    assert v.start == start and v.granularity is TimeGranularity.DAY
    assert not v.needs_confirmation


def test_date_and_clock_merge():
    v = one("거래일시 2026-06-01 14:05")
    assert (v.start, v.end) == (datetime(2026, 6, 1, 14, 5), datetime(2026, 6, 1, 14, 6))
    assert v.granularity is TimeGranularity.MINUTE


def test_messenger_clock_takes_date_from_anchor():
    v = one("[찬찬] [오후 1:52] 계좌는 제 명의예요", Anchor(date(2026, 6, 1), "message_date"))
    assert v.kind is TimeKind.CONTEXTUAL
    assert v.start == datetime(2026, 6, 1, 13, 52)


def test_clock_without_ampm_keeps_both_readings():
    v = one("2026년 6월 1일 3시 20분")
    assert v.start == datetime(2026, 6, 1, 3, 20)
    assert [c.start for c in v.candidates] == [datetime(2026, 6, 1, 15, 20)]
    later = one("2026년 6월 1일 15:20")
    assert v.compatible(later)


def test_approximate_time_widens_interval():
    v = one("2026년 6월 1일 오후 2시경")
    assert v.start == datetime(2026, 6, 1, 13) and v.end == datetime(2026, 6, 1, 16)
    assert v.approximate


def test_lunar_date_converted():
    v = one("음력 2023년 8월 15일")
    assert v.kind is TimeKind.LUNAR
    assert v.start == datetime(2023, 9, 29)


def test_lunar_leap_month():
    v = one("윤2월 10일(음)", Anchor(date(2023, 5, 1), "document_date"))
    assert v.kind is TimeKind.LUNAR and v.start == datetime(2023, 3, 31)
    missing = one("윤2월 10일(음)")  # 2026년에는 윤2월이 없다
    assert missing.kind is TimeKind.UNRESOLVED and missing.needs_confirmation


def test_deictic_relative_uses_document_date():
    v = one("지난주 금요일 경찰서에 전화함")
    assert v.kind is TimeKind.RELATIVE and v.start == datetime(2026, 5, 29)
    assert one("3일 전에 송금").start == datetime(2026, 6, 1)
    assert one("어제 연락").start == datetime(2026, 6, 3)
    assert one("작년 3월에 고소").start == datetime(2025, 3, 1)


def test_anaphoric_relative_uses_last_mentioned_date():
    mentioned = Anchor(date(2026, 6, 1), "mentioned_date")
    v = one("그 다음날 다시 연락했다", DOC, mentioned)
    assert v.start == datetime(2026, 6, 2) and not v.needs_confirmation
    fallback = one("그 다음날 다시 연락했다", DOC, None)
    assert fallback.needs_confirmation


def test_weak_anchor_needs_confirmation():
    v = one("어제 전화함", Anchor(date(2026, 6, 20), "capture_date"))
    assert v.start == datetime(2026, 6, 19) and v.needs_confirmation


def test_invalid_date_gives_candidates_not_a_guess():
    v = one("2026.13.05 에 접수")
    assert v.kind is TimeKind.CORRECTED and v.needs_confirmation
    assert v.start is None
    days = {c.start.date() for c in v.candidates}
    assert {date(2026, 1, 5), date(2026, 3, 5), date(2026, 5, 13)} <= days


def test_weekday_mismatch_flagged():
    v = one("2026. 6. 3.(월) 신고")
    assert v.kind is TimeKind.CORRECTED and v.needs_confirmation
    assert all(c.start.weekday() == 0 for c in v.candidates[1:])
    assert v.candidates[0].start == datetime(2026, 6, 3)


def test_ocr_letter_digit_confusion_is_corrected_but_flagged():
    v = one("2O26.06.01 이체")
    assert v.start == datetime(2026, 6, 1)
    assert v.kind is TimeKind.CORRECTED and v.needs_confirmation


@pytest.mark.parametrize(
    "text", ["3시간 동안 기다렸다", "350,000원 국민 940*-**-****21", "접수번호 2026-0603-123", "오늘날 사회"]
)
def test_non_time_expressions_ignored(text):
    assert N.extract(text, DOC) == []


def test_partial_date_year_inferred_toward_past():
    v = one("12월 25일에 만났다", Anchor(date(2026, 6, 4), "document_date"))
    assert v.kind is TimeKind.PARTIAL and v.start == datetime(2025, 12, 25)


def test_daypart_attaches_to_date():
    v = one("6/2 저녁 전화 안받음")
    assert v.start == datetime(2026, 6, 2, 17) and v.end == datetime(2026, 6, 2, 22)
