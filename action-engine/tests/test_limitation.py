"""공소시효 계산 테스트."""

from datetime import date

from action_engine.limitation import compute_limitation, find_offence, load_offences

TODAY = date(2026, 9, 12)


# ── 죄명 찾기 ───────────────────────────────────────────────────────────


def test_별칭으로도_찾는다():
    assert find_offence("살인")["statute"] == "형법 제250조 제1항"
    assert find_offence("살인죄")["statute"] == "형법 제250조 제1항"


def test_표에_없는_죄명은_계산하지_않는다():
    """비슷해 보이는 죄명으로 대신 계산하면 안 된다. 한 구간만 달라도 시효가 5년 이상 차이 난다."""
    assert find_offence("상해치사") is None  # not_filled 에 있다
    r = compute_limitation("상해치사", date(2010, 1, 1), TODAY)
    assert r["resolved"] is False
    assert "찾지 못했" in r["reason"]


def test_죄명이_없으면_계산하지_않는다():
    r = compute_limitation(None, date(2010, 1, 1), TODAY)
    assert r["resolved"] is False
    assert "죄명 정보가 없어" in r["reason"]


# ── 시효 폐지 ───────────────────────────────────────────────────────────


def test_살인은_시효가_폐지되었다():
    r = compute_limitation("살인", date(1998, 5, 1), TODAY)
    assert r["resolved"] is True
    assert r["abolished"] is True
    assert "제253조의2" in r["basis"]
    assert "이미 시효가 완성된 사건" in r["note"]  # 무조건 폐지가 아니라는 경고


def test_강도치사는_폐지_대상이_아니다():
    """살해의 고의가 없으므로 시효가 남아 있다."""
    r = compute_limitation("강도치사", date(2015, 1, 1), TODAY)
    assert r["abolished"] is False
    assert r["years"] == 15  # 무기징역 구간 · 신법


# ── 개정 전후 ───────────────────────────────────────────────────────────


def test_2007년_이전_범행은_구법을_쓴다():
    """장기·미제 사건에서 제일 위험한 실수. 신법으로 계산하면 이미 끝난 사건을 살아 있다고 안내한다."""
    old = compute_limitation("강도치사", date(2005, 6, 1), TODAY)
    assert old["version"] == "old"
    assert old["years"] == 10  # 구법 무기징역 10년
    assert old["due_date"] == date(2015, 6, 1)
    assert old["days_left"] < 0  # 이미 만료
    assert "개정 전" in old["version_note"]


def test_2007년_이후_범행은_신법을_쓴다():
    new = compute_limitation("강도치사", date(2020, 6, 1), TODAY)
    assert new["version"] == "current"
    assert new["years"] == 15
    assert new["due_date"] == date(2035, 6, 1)
    assert new["days_left"] > 0


def test_같은_죄명이라도_범행일에_따라_5년_차이가_난다():
    a = compute_limitation("강도치사", date(2007, 12, 21), TODAY)  # 개정일 당일 — 구법
    b = compute_limitation("강도치사", date(2007, 12, 22), TODAY)  # 하루 뒤 — 신법
    assert a["years"] == 10
    assert b["years"] == 15


# ── 계산 ────────────────────────────────────────────────────────────────


def test_범행일을_모르면_계산하지_않는다():
    r = compute_limitation("강도치사", None, TODAY)
    assert r["resolved"] is False
    assert "범행 종료일" in r["reason"]


def test_시효정지는_빼지_않았다고_알린다():
    """사용자가 알기 어려운 정보라 계산에 넣지 않았다. 그 사실을 숨기지 않는다."""
    r = compute_limitation("강도치사", date(2020, 1, 1), TODAY)
    assert "정지" in r["caveat"]


def test_윤년_2월29일도_계산된다():
    r = compute_limitation("강도치사", date(2020, 2, 29), TODAY)
    assert r["due_date"] == date(2035, 2, 28)


# ── 데이터 ──────────────────────────────────────────────────────────────


def test_모든_죄명에_근거와_출처가_있다():
    for row in load_offences()["offences"]:
        assert row["statute"], f"{row['name']} 에 조문이 없습니다"
        assert row["source"], f"{row['name']} 에 출처가 없습니다"
        assert row["bracket"], f"{row['name']} 에 법정형 구간이 없습니다"


def test_못채운_죄명은_이유와_함께_남긴다():
    """조용히 빼지 않는다. 무엇이 왜 없는지 보여야 다음 사람이 채운다."""
    gaps = load_offences()["not_filled"]
    assert gaps
    for g in gaps:
        assert g["why"]
