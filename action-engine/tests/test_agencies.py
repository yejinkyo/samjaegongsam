"""기관 조회 테스트."""

from action_engine.agencies import describe_submit_to, find_agency, find_parent, load_agencies


def test_경찰서를_이름으로_찾는다():
    """'대구중부', '대구중부경찰서' 둘 다 받는다."""
    assert find_agency("대구중부")["name"] == "대구중부경찰서"
    assert find_agency("대구중부경찰서")["name"] == "대구중부경찰서"


def test_상급관서를_찾는다():
    """수사중지 이의제기서를 내는 곳이다 (경찰수사규칙 제101조)."""
    assert find_parent("대구중부")["name"] == "대구광역시경찰청"


def test_상급경찰관서_문구에_실제_관서를_붙인다():
    r = describe_submit_to("해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장", "대구수성")
    assert r["resolved"] is True
    assert r["target"]["name"] == "대구광역시경찰청"
    assert r["station"]["name"] == "대구수성경찰서"
    assert "송부" in r["hint"]


def test_그냥_경찰서에_내는_절차는_그_경찰서를_가리킨다():
    r = describe_submit_to("불송치 결정을 한 사법경찰관의 소속 관서의 장", "대구달서")
    assert r["resolved"] is True
    assert r["target"]["name"] == "대구달서경찰서"


def test_자료에_없는_지역은_지어내지_않는다():
    """수집한 지역 밖이면 원래 문구만 보여준다."""
    r = describe_submit_to("바로 위 상급경찰관서의 장", "서울강남")
    assert r["resolved"] is False
    assert "기관 자료에 없습니다" in r["reason"]
    assert "대구광역시경찰청" in r["reason"]  # 어디까지 수집했는지 알려준다


def test_경찰서를_모르면_계산하지_않는다():
    r = describe_submit_to("바로 위 상급경찰관서의 장", None)
    assert r["resolved"] is False
    assert "알 수 없습니다" in r["reason"]


def test_경찰서_주소는_아직_비어있다():
    """원자료에 지구대 주소만 있고 경찰서 자체 주소가 없다. 그 사실을 숨기지 않는다."""
    kb = load_agencies()
    assert kb["status"] == "partial"
    station = find_agency("대구중부")
    assert station["address"] is None
    assert "경찰서 자체의 주소" in kb["known_gaps"][0]


def test_지역경찰관서는_주소가_있다():
    """지구대·파출소 주소는 원자료에 있다. 나중에 관할 추정에 쓸 수 있다."""
    offices = find_agency("대구중부")["local_offices"]
    assert offices
    assert all(o["address"] for o in offices)
    assert any("중구" in o["address"] for o in offices)
