"""5단계 — 필요 서류 ↔ 자료함 대조 테스트."""

from action_engine import build_card, build_checklist
from action_engine.checklist import load_documents
from action_engine.schema import Deadline

DOCS = [
    {"doc_id": "notice1", "doc_type": "notice"},
    {"doc_id": "receipt1", "doc_type": "receipt"},
    {"doc_id": "kakao1", "doc_type": "messenger"},
]

ITEMS = [
    {"항목": "수사중지 결정 통지서 사본", "필수": True, "생성가능": False, "대응_자료종류": ["notice"]},
    {"항목": "재수사 요청서", "필수": True, "생성가능": True, "대응_자료종류": []},
    {"항목": "진술조서 사본", "필수": False, "생성가능": False, "대응_자료종류": ["statement"]},
    {"항목": "통신사실확인자료", "필수": False, "생성가능": False, "대응_자료종류": ["messenger"]},
]


def _kb(monkeypatch, items):
    from action_engine import checklist as C

    C.load_documents.cache_clear()
    monkeypatch.setattr(C, "load_documents", lambda: {"actions": {"ACT-테스트": {"items": items}}})


# ── 지식베이스가 비었을 때 (지금 상태) ──────────────────────────────────


def test_필요서류가_비어있으면_체크리스트를_만들지_않는다():
    """기한과 같은 원칙. 없는 것을 지어내면 신청이 반려된다."""
    c = build_checklist("ACT-근거보완", DOCS)
    assert c.items == []
    assert c.total == 0
    assert "법령·서식 확인" in c.unresolved


def test_서류를_채웠으면_근거가_붙는다():
    """채운 액션에는 서식명과 제출처가 있어야 한다. 비운 액션에는 무엇을 확인할지가 있어야 한다."""
    kb = load_documents()
    assert kb["status"] == "draft_unverified"  # 법률 전문가 검수 전
    for action, entry in kb["actions"].items():
        if entry.get("items"):
            assert entry.get("form_name"), f"{action} 에 서식명이 없습니다"
            assert entry.get("submit_to"), f"{action} 에 제출처가 없습니다"
        elif not entry.get("by_stage"):
            assert entry.get("check"), f"{action} 에 무엇을 확인해야 하는지가 없습니다"


def test_단계마다_서류가_다르면_ST로_갈라_조회한다():
    """'불복'은 불송치면 이의신청서, 불기소면 항고장, 수사중지면 이의제기서다."""
    c1 = build_checklist("ACT-불복기한", DOCS, st="ST-301")
    assert c1.form_name == "불송치 결정 이의신청서"
    assert "경찰수사규칙 별지" not in (c1.form_url or "")  # URL 은 다운로드 주소다
    assert c1.form_url and c1.form_url.startswith("http")

    c2 = build_checklist("ACT-불복기한", DOCS, st="ST-201")
    assert c2.form_name == "수사중지 결정 이의제기서"
    assert "상급경찰관서" in c2.submit_to

    c3 = build_checklist("ACT-불복기한", DOCS, st="ST-302")
    assert c3.form_name == "항고장"
    assert "고등검찰청" in c3.submit_to


def test_아직_못_채운_액션은_체크리스트를_만들지_않는다():
    c = build_checklist("ACT-근거보완", DOCS)
    assert c.items == []
    assert "확인 필요" in c.unresolved


def test_재정신청은_선행절차를_알려준다():
    c = build_checklist("ACT-불복기한", DOCS, st="ST-303")
    assert c.form_name == "재정신청서"
    assert c.prerequisite and "항고" in c.prerequisite


def test_모르는_액션도_깨지지_않는다():
    assert build_checklist("ACT-없는것", DOCS).unresolved
    assert build_checklist(None, DOCS).unresolved


# ── 지식베이스가 채워졌을 때 (미리 고정) ────────────────────────────────


def test_자료함에_있으면_보유로_잡는다(monkeypatch):
    _kb(monkeypatch, ITEMS)
    c = build_checklist("ACT-테스트", DOCS)
    by = {i.label: i for i in c.items}
    assert by["수사중지 결정 통지서 사본"].state == "보유"
    assert by["수사중지 결정 통지서 사본"].doc_ids == ["notice1"]


def test_없으면_미보유_생성가능하면_생성가능(monkeypatch):
    _kb(monkeypatch, ITEMS)
    by = {i.label: i for i in build_checklist("ACT-테스트", DOCS).items}
    assert by["진술조서 사본"].state == "미보유"  # 대응 자료가 없다
    assert by["재수사 요청서"].state == "생성가능"  # 확보된 사실로 초안을 만들 수 있다


def test_보존기한이_지났으면_확보불가로_내린다(monkeypatch):
    """장기미제에서 '없다'와 '더는 구할 수 없다'는 다른 정보다."""
    _kb(monkeypatch, ITEMS)
    expired = [Deadline(code="TIM-031", label="디지털 보존", severity="expired")]
    docs = [d for d in DOCS if d["doc_type"] != "messenger"]  # 통신자료가 자료함에 없다
    by = {i.label: i for i in build_checklist("ACT-테스트", docs, expired).items}
    assert by["통신사실확인자료"].state == "확보불가"
    assert "보존 기한" in by["통신사실확인자료"].reason


def test_보유하고_있으면_기한이_지나도_보유다(monkeypatch):
    _kb(monkeypatch, ITEMS)
    expired = [Deadline(code="TIM-031", label="디지털 보존", severity="expired")]
    by = {i.label: i for i in build_checklist("ACT-테스트", DOCS, expired).items}
    assert by["통신사실확인자료"].state == "보유"  # 이미 확보했으면 기한과 무관


def test_준비율을_센다(monkeypatch):
    _kb(monkeypatch, ITEMS)
    c = build_checklist("ACT-테스트", DOCS)
    assert (c.done, c.total) == (2, 4)  # 통지서 · 통신자료 보유


def test_필수여부가_실린다(monkeypatch):
    _kb(monkeypatch, ITEMS)
    by = {i.label: i for i in build_checklist("ACT-테스트", DOCS).items}
    assert by["수사중지 결정 통지서 사본"].required is True
    assert by["진술조서 사본"].required is False


# ── 카드에 실린다 ───────────────────────────────────────────────────────


def test_카드에_체크리스트가_붙는다(missing, fraud):
    for result in (missing, fraud):
        card = build_card(result)
        assert card.checklist is not None
        assert card.checklist.action == card.next_action.action
        # 지금은 지식베이스가 비어 있으므로 항목이 없는 것이 정상이다
        assert card.checklist.unresolved
