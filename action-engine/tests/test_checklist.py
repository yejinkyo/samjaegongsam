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
    c = build_checklist("ACT-기록열람", DOCS)
    assert c.items == []
    assert c.total == 0
    assert "법령·서식 확인" in c.unresolved


def test_모든_액션의_필요서류가_비어있다():
    """값을 추측으로 채우지 않았다는 것을 테스트로 고정한다."""
    kb = load_documents()
    assert kb["status"] == "draft_unverified"
    for action, entry in kb["actions"].items():
        assert entry["items"] == [], f"{action} 에 검수 안 된 서류가 들어갔습니다"
        assert entry["check"], f"{action} 에 무엇을 확인해야 하는지가 없습니다"


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
