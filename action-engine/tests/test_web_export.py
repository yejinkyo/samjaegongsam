"""화면 데이터 내보내기 테스트 — tools/export_web.py.

화면은 이 데이터만 읽는다. 그래서 여기서 막아야 할 것은 둘이다.
절차를 지어내지 않는가, 그리고 커밋된 web/data/cases.js 가 엔진 출력과 어긋나지 않았는가.
"""

import importlib.util
import json
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "export_web.py"


@pytest.fixture(scope="module")
def export():
    spec = importlib.util.spec_from_file_location("export_web", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def views(export):
    return {v["id"]: v for v in export.build_all()}


def test_예시_사건을_모두_내보낸다(export, views):
    """세 건은 반드시 있다. 직접 만든 사건을 얹었으면 더 있을 수 있다(EXTRA_CASES)."""
    assert {case_id for case_id, _ in export.CASES} <= set(views)
    for v in views.values():
        assert v["stages"] and v["timeline"] and v["issues"]
        assert v["next_action"] is not None


def test_직접_만든_사건이_없으면_세_건만_나온다(export, views, monkeypatch):
    """목록 파일이 없을 때 지금까지와 똑같이 도는지 — 있던 동작을 바꾸지 않는다."""
    monkeypatch.setattr(export, "EXTRA_CASES", export.ROOT / "없는파일.json")
    assert {v["id"] for v in export.build_all()} == {case_id for case_id, _ in export.CASES}


def test_사건_하나만_화면_데이터로_바꾼다(export, monkeypatch, tmp_path):
    """화면에서 등록한 사건은 서버가 --result 로 하나씩 넘긴다. cases.js 는 건드리지 않는다."""
    out = tmp_path / "view.json"
    monkeypatch.setattr(export, "OUT", tmp_path / "cases.js")
    monkeypatch.setattr("sys.argv", ["export_web.py", "--result", str(export.FIXTURES / "long_unsolved_missing.json"),
                                     "--id", "u1", "--title", "내가 올린 사건", "--out", str(out)])
    export.main()
    view = json.loads(out.read_text(encoding="utf-8"))
    assert view["id"] == "u1" and view["title"] == "내가 올린 사건"
    assert view["type"] == "missing_person_suspended" and view["timeline"]
    assert not (tmp_path / "cases.js").exists()


def test_절차가_확인되지_않았으면_칸을_채우지_않는다(views):
    """피그마 시안의 예시 문구(무엇을·어디에·어떻게·언제까지)를 대신 넣으면 안 된다."""
    na = views["used_goods_fraud"]["next_action"]
    assert na["state"] == "unresolved"
    assert na["rows"] == []
    assert na["prepare"] is None


def test_채워진_절차는_지식베이스_값만_싣는다(views):
    na = views["suspension_recent"]["next_action"]
    assert na["state"] == "filled"
    keys = [r["k"] for r in na["rows"]]
    assert keys[:2] == ["무엇을", "어디에"]
    assert "어떻게" not in keys  # 지식베이스에 없는 칸은 만들지 않는다
    assert na["due"]["label"].startswith("D-")
    assert na["prepare"]["total"] == 2


def test_어긋난_자료의_사건을_표시한다(views):
    events = [row for row in views["used_goods_fraud"]["timeline"] if row["type"] == "event"]
    conflicted = {row["title"] for row in events if row["conflict"]}
    assert conflicted == {"300,000원 송금", "350,000원 송금"}


def test_기록_공백은_시간순으로_끼워_넣는다(views):
    rows = views["long_unsolved_missing"]["timeline"]
    assert any(row["type"] == "gap" for row in rows)
    first_gap = next(i for i, row in enumerate(rows) if row["type"] == "gap")
    assert rows[first_gap - 1]["type"] == "event"  # 공백 앞에는 그 전의 사건이 온다


def test_자정을_넘는_시간대를_어색하게_적지_않는다(views):
    times = [row["time"] for row in views["long_unsolved_missing"]["timeline"] if row["type"] == "event"]
    assert not any("~0시" in t for t in times)
    assert any("익일" in t or "24시" in t for t in times)


def test_커밋된_화면_데이터가_엔진_출력과_같다(export):
    """엔진이나 픽스처를 고치고 export_web.py 를 다시 돌리지 않으면 여기서 걸린다."""
    assert export.OUT.read_text(encoding="utf-8") == export.render(export.build_all())
