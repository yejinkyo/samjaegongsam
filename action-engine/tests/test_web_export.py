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


def test_절차가_확인되지_않았으면_칸을_채우지_않는다(export, monkeypatch):
    """피그마 시안의 예시 문구(무엇을·어디에·어떻게·언제까지)를 대신 넣으면 안 된다."""
    from action_engine import checklist

    monkeypatch.setattr(checklist, "load_documents", lambda: {"actions": {}})
    na = {v["id"]: v for v in export.build_all()}["used_goods_fraud"]["next_action"]
    assert na["state"] == "unresolved"
    assert na["rows"] == []
    assert na["prepare"] is None


def test_모순확인은_자료_의견_제출서로_채운다(views):
    """수사준칙 제25조 — 법정 서식이 없어 서면 제출로 안내한다."""
    na = views["used_goods_fraud"]["next_action"]
    assert na["state"] == "filled"
    rows = {r["k"]: r["v"] for r in na["rows"]}
    assert rows["무엇을"] == "자료·의견 제출서"
    assert "제25조" in rows["근거"]


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
    screen_views = [v for v in export.build_all() if v["id"] not in export.SKIP_ON_SCREEN]
    assert export.OUT.read_text(encoding="utf-8") == export.render(screen_views)


# ── 타임라인 줄 이름 ─────────────────────────────────────────────────────


def _one_event(doc_type: str, lines: list[str], line_no: int, *, stage="occurrence", kind=None, time=None, issued=None):
    doc = {"doc_id": "d", "doc_type": doc_type, "lines": [{"line_no": i + 1, "text": t} for i, t in enumerate(lines)]}
    event = {"stage": stage, "title": lines[line_no - 1], "time": {"start": time} if time else None,
             "event_ids": ["d:e1"], "evidence_level": "statement",
             "sources": [{"source_doc_id": "d", "source_line": line_no, "quote": lines[line_no - 1]}]}
    result = {"extraction": {"events": [{"event_id": "d:e1", "action_kind": kind}], "mentions": [],
                             "document_dates": {"d": {"value": {"start": issued}}} if issued else {}}}
    return event, result, {"d": doc}


def test_양식_문서는_그_문서가_뜻하는_일로_적는다(export):
    """유전자 채취 확인서의 '대상자 …' 줄을 그대로 붙이면 무슨 일이었는지 알 수 없다."""
    lines = ["유전자 검사 대 상물 채취 확인서", "관리번호 2025-DNA-0142", "대상자 조말순 (실종자 임세진의 모)",
             "위 대상물은 실종아동등 프로파일링시스템 등록을 위하여", "채취되었음을 확인합니다."]
    assert export._summary(*_one_event("unknown", lines, 3, kind="disappearance")) == "DNA 채취 — 실종자 유전자 등록"


def test_양식에_적힌_다른_날의_일은_그_일로_적는다(export):
    """접수증에 적힌 '최종목격 11/4 23:20' 을 '실종신고 접수'로 적으면 날짜와 일이 어긋난다."""
    lines = ["실종신고 접수증", "접수일시 2006. 11. 6.", "최종목격 ㅣ 2006. 11. 4. 23:20경 ○○천 제방길"]
    event = _one_event("receipt", lines, 3, kind="sighting", time="2006-11-04T23:20:00", issued="2006-11-06T00:00:00")
    assert export._summary(*event) == "마지막 목격 · ○○천 제방길"


def test_통지서는_결정_내용을_함께_적는다(export):
    lines = ["수사결과 통지서", "사건번호 2019형제20447", "결정 내용 수사중지(참고인중지)"]
    assert export._summary(*_one_event("notice", lines, 1, stage="outcome")) == "수사결과 통지 — 수사중지(참고인중지)"


def test_사람이_쓴_글의_둘째_줄을_문서_제목으로_읽지_않는다(export):
    lines = ["15년 10월 10일 밤 연락 끊김", "10월 12일 경찰서 실종신고"]
    assert export._summary(*_one_event("memo", lines, 1, kind="contact_lost")) == "연락 두절"


def test_요약할_수_없으면_지어내지_않는다(export):
    """표에 없는 일은 None — 화면은 원문 첫 문장을 쓴다."""
    assert export._summary(*_one_event("statement", ["그날 날씨가 흐렸습니다."], 1)) is None


def test_타임라인은_요약을_싣고_원문은_자세히에_둔다(views):
    events = [r for r in views["long_unsolved_missing"]["timeline"] if r["type"] == "event"]
    titles = {r["title"] for r in events}
    assert {"연락 두절", "실종신고 접수", "마지막 목격 · ○○역 인근", "재수사 요청"} <= titles
    notice = next(r for r in events if r["title"].startswith("수사결과 통지"))
    assert notice["full"] == "수사결과 통지서"  # 원문은 그대로 남는다


def test_재판_단계_사건은_범위_밖이라고_화면에_알린다(export):
    """재판이 시작된 사건에 '수사기관에 새 정보 제출'을 띄우면 엉뚱한 곳에 내게 된다."""
    import copy

    result = copy.deepcopy(json.loads((export.FIXTURES / "suspension_recent.json").read_text(encoding="utf-8")))
    for slot in result["analysis"]["slot_statuses"]:
        if slot["slot"] == "decision_type":
            slot["value"], slot["state"] = "구공판(공소제기)", "confirmed"
    na = export.build_view("trial", "재판 중인 사건", result)["next_action"]
    assert na["action"] == "ACT-재판단계"
    assert "범위 밖" in na["label"]
    assert na["state"] == "no_submission" and "제294조의4" in na["note"]
    assert na["also"] == []  # 수사기관에 낼 행동을 참고사항으로도 띄우지 않는다
    assert na["draft"] is None


# ── 낸 것 · 받은 답에 따라 다음 단계로 ──────────────────────────────────


def test_답마다_그_단계에_맞는_행동_목록을_싣는다(views):
    """화면은 엔진을 부를 수 없다. 답을 기록하면 엔진이 그 답으로 미리 계산한 목록을 그대로 쓴다.

    옛 카드의 행을 쓰면 불기소를 받은 뒤에도 '이의제기서 · 상급경찰관서'를 안내하게 된다.
    """
    outcomes = views["suspension_recent"]["outcomes"]

    def first(choice):
        a = outcomes[choice]["actions"][0]
        return a["action"], {r["k"]: r["v"] for r in a["rows"]}.get("무엇을"), a["due_rule"]

    assert first("불기소") == ("ACT-불복기한", "항고장", {"label": "검찰 항고 기한", "period_days": 30})
    assert first("항고 기각")[1:] == ("재정신청서", {"label": "법원 재정신청 기한", "period_days": 10})
    assert first("참고인중지")[1] == "수사중지 결정 이의제기서"
    assert first("기소")[0] == "ACT-재판단계"


def test_답의_기한은_날짜로_굳히지_않는다(views):
    """미리 계산할 때는 기준일에 받았다고 둔다. 실제로 받은 날은 사용자가 고르므로 화면이 기간을 더한다."""
    for outcome in views["suspension_recent"]["outcomes"].values():
        for a in outcome["actions"]:
            assert a["due"] is None
            assert "언제까지" not in [r["k"] for r in a["rows"]]


def test_타임라인_줄에_날짜를_싣는다(views):
    """화면이 낸 것 · 받은 답을 날짜 순서대로 끼워 넣을 수 있어야 한다."""
    rows = views["long_unsolved_missing"]["timeline"]
    dated = [r["at"] for r in rows if r.get("at")]
    assert dated == sorted(dated)
    assert all(r["at"] is None for r in rows if r["type"] == "event" and r["time"] == "시각 미상")


def test_급함_기준을_화면에_넘긴다(views):
    assert views["suspension_recent"]["severity_days"] == {"critical": 7, "soon": 30}


def test_답으로_기록한_결정의_통지서를_가진_것으로_보지_않는다(views):
    """자료함의 통지서는 이전 결정의 것이다. 새 통지서는 올리기 전까지 없다."""
    a = views["suspension_recent"]["outcomes"]["불기소"]["actions"][0]
    notice = next(i for i in a["prepare"]["items"] if "통지서" in i["label"])
    assert notice["state"] == "미보유"
    assert a["prepare"]["done"] == sum(1 for i in a["prepare"]["items"] if i["state"] == "보유")


def test_답의_기한에는_통지_수령일부터_세는_것만_싣는다(views):
    """화면은 고른 수령일에 기간을 더한다. 공소시효(범행 종료일부터 N년)를 실으면 수령일 + 10년이 된다."""
    for outcome in views["suspension_recent"]["outcomes"].values():
        assert "형사 공소시효 임박" not in [t["label"] for t in outcome["deadlines"]]
    assert [t["label"] for t in views["suspension_recent"]["outcomes"]["불기소"]["deadlines"]] == ["검찰 항고 기한"]


# ── 화면 말 ────────────────────────────────────────────────────────────


def test_엔진_점수와_자료_id_를_화면에_싣지_않는다(export):
    docs = {"news_2018": {"file_name": "기사_2018.jpg"}}
    text = ("최종 목격 일시: 차이가 있어 보입니다 — ‘11-02’(news_2018 · 3줄) "
            "(모순 점수 0.54 < 기준 0.70; 추출 신뢰도 낮음: news_2018 · 3줄 (0.60))")
    assert export._plain(text, docs) == "최종 목격 일시: 차이가 있어 보입니다 — ‘11-02’(기사_2018.jpg · 3줄)"
    # 판정 근거가 아닌 괄호는 그대로 둔다
    assert export._plain("읽히지 않은 부분이 1곳 있습니다 (7줄)", docs) == "읽히지 않은 부분이 1곳 있습니다 (7줄)"


def test_항목과_상태_이름을_모두_한국어로_옮긴다(export):
    assert export.SLOT_LABELS["offence"] == "죄명"
    assert export.SLOT_STATES["unreadable"][0] == "읽히지 않음"
