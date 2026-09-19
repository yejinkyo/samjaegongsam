"""5단계 — 필요 서류 ↔ 자료함 대조 테스트."""

import pytest

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


# ── 지식베이스가 비었을 때 ──────────────────────────────────────────────


def test_필요서류가_비어있으면_체크리스트를_만들지_않는다(monkeypatch):
    """기한과 같은 원칙. 없는 것을 지어내면 신청이 반려된다."""
    from action_engine import checklist as C

    monkeypatch.setattr(C, "load_documents", lambda: {"actions": {"ACT-테스트": {"check": "법령·서식 확인 필요"}}})
    c = build_checklist("ACT-테스트", DOCS)
    assert c.items == []
    assert c.total == 0
    assert "법령·서식 확인" in c.unresolved


def test_서류를_채웠으면_근거가_붙는다():
    """채운 액션에는 서식명·제출처·근거가 있어야 한다. 비운 액션에는 무엇을 확인할지가 있어야 한다."""
    kb = load_documents()
    assert kb["status"] == "verified"
    assert "법률 전문가 검토는 아니다" in kb["verified_scope"]  # 조문 대조까지만 했다는 것을 숨기지 않는다
    assert kb["verified_laws"] and all(law["MST"] and law["시행일자"] for law in kb["verified_laws"])
    for action, entry in kb["actions"].items():
        if entry.get("items"):
            assert entry.get("form_name"), f"{action} 에 서식명이 없습니다"
            if entry.get("statute"):  # 온라인 조회(단계확인)는 서식이 아니다
                assert entry.get("form_source"), f"{action} 에 서식 근거가 없습니다"
            assert entry.get("submit_to"), f"{action} 에 제출처가 없습니다"
            assert entry.get("statute") or entry.get("source"), f"{action} 에 근거 법령도 출처도 없습니다"
            assert entry.get("verified", {}).get("at"), f"{action} 을 언제 무엇과 대조했는지가 없습니다"
        elif entry.get("no_submission"):
            assert entry.get("why"), f"{action} 에 제출 서류가 없는 이유가 없습니다"
        elif not entry.get("by_stage"):
            assert entry.get("check"), f"{action} 에 무엇을 확인해야 하는지가 없습니다"


def test_제출서류가_없는_단계는_못채움과_구별한다():
    """'제출할 서류가 원래 없음'과 '아직 못 채움'은 다른 상태다.

    자료를 확보하는 단계에 "법령·서식 확인 필요"를 띄우면, 사용자는 뭔가 빠진 줄 알고 멈춘다.
    """
    c = build_checklist("ACT-근거보완", DOCS)
    assert c.items == []
    assert c.unresolved is None
    assert c.no_submission and "확보" in c.no_submission

    for action in ("ACT-근거보완", "ACT-공백보완"):
        entry = load_documents()["actions"][action]
        assert entry.get("routes"), f"{action} 에 자료를 얻는 공식 경로가 없습니다"
        assert all(r.get("statute") for r in entry["routes"])


def test_피해자가_청구할_수_없는_증거보전은_안내하지_않는다():
    """형사소송법 제184조 제1항 — 청구권자는 검사·피고인·피의자·변호인뿐이다."""
    entry = load_documents()["actions"]["ACT-증거보존"]
    assert any("제184조" in r["statute"] for r in entry["not_available"])

    c = build_checklist("ACT-증거보존", DOCS)
    assert not any("증거보전" in i.label for i in c.items)
    assert c.form_name == "자료·의견 제출서"  # 대신 수사기관에 보존·확보를 요청한다 (수사준칙 제25조)
    assert "제25조" in c.statute


def test_시효임박_재정신청은_불기소_단계에만_연결한다():
    """형사소송법 제260조 제2항 제3호 — 항고 없이, 공소시효 만료일 전날까지.

    제1항이 '공소를 제기하지 아니한다는 통지를 받은 때'를 요건으로 두므로 불기소(ST-302)에만 붙인다.
    """
    c = build_checklist("ACT-공소시효", DOCS, st="ST-302")
    assert c.form_name == "재정신청서"
    assert "제3호" in c.statute
    assert c.prerequisite and "항고를 거치지 않아도" in c.prerequisite
    assert c.advisory and "전날까지" in c.advisory
    assert c.source and c.source.startswith("https://www.law.go.kr")

    police = build_checklist("ACT-공소시효", DOCS, st="ST-201")
    assert police.form_name == "자료·의견 제출서"  # 불기소 통지 전에는 재정신청을 할 수 없다
    assert not any("재정신청" in i.label for i in police.items)


def test_단계확인은_사건조회_경로와_출처를_준다():
    c = build_checklist("ACT-단계확인", DOCS)
    assert "사건조회" in c.form_name
    assert "kics.go.kr" in c.submit_to
    assert c.source and c.source.startswith("https://www.gov.kr")
    by = {i.label: i for i in c.items}
    assert by["사건 접수증 또는 통지서"].state == "보유"  # 접수증이 자료함에 있다
    assert by["인증서 (형사사법포털 로그인용)"].required is True


def test_정정_내역을_기록으로_남긴다():
    """확인 메모를 고친 곳은 근거와 함께 남긴다. 같은 오류가 다시 들어오지 않게 하기 위해서다."""
    corrections = load_documents()["corrections"]
    assert len(corrections) >= 2
    for c in corrections:
        assert c["fixed"] and c["why_it_matters"] and c["verified_at"]


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


def test_검사의_기소중지는_항고장으로_간다():
    """검찰사건사무규칙 제147조 제1항 — 기소중지·참고인중지도 불기소결정이라 항고 대상이다."""
    police = build_checklist("ACT-불복기한", DOCS, st="ST-201", issuer="police")
    assert police.form_name == "수사중지 결정 이의제기서"
    prosecution = build_checklist("ACT-불복기한", DOCS, st="ST-201", issuer="prosecution")
    assert prosecution.form_name == "항고장"
    assert "고등검찰청" in prosecution.submit_to


def test_비어_있던_여섯_행동이_모두_채워졌다():
    """제출 서류가 있는 넷은 서식·제출처·근거를, 자료를 확보하는 둘은 공식 경로를 준다."""
    for action in ("ACT-신규정보제출", "ACT-모순확인", "ACT-공소시효", "ACT-증거보존"):
        c = build_checklist(action, DOCS)
        assert c.unresolved is None, action
        assert c.form_name and c.submit_to and c.statute, action
        assert c.reason_heading == "요청 사항" and c.reason_note, action
        assert any(i.state == "생성가능" for i in c.items), action
    for action in ("ACT-근거보완", "ACT-공백보완"):
        c = build_checklist(action, DOCS)
        assert c.unresolved is None and c.no_submission, action


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
        # 두 사건의 다음 행동(신규정보제출 · 모순확인)은 수사준칙 제25조의 자료·의견 제출로 채워져 있다
        assert card.checklist.unresolved is None
        assert card.checklist.form_name == "자료·의견 제출서"


@pytest.mark.parametrize("st, statute", [("ST-401", "제294조의4"), ("ST-402", "제59조의2"), ("ST-403", "제424조")])
def test_재판_단계는_범위_밖이라고_알리고_법원_경로를_준다(st, statute):
    c = build_checklist("ACT-재판단계", DOCS, st=st)
    assert c.no_submission and "범위 밖" in c.no_submission
    assert statute in c.no_submission


@pytest.mark.parametrize("st, word", [("ST-101", "고소"), ("ST-102", "경찰수사규칙 제11조"), ("ST-103", "수사준칙 제12조")])
def test_수사_중에는_단계에_맞는_진행상황_확인_경로를_준다(st, word):
    c = build_checklist("ACT-진행확인", DOCS, st=st)
    assert c.no_submission and word in c.no_submission
