"""research-engine 이 선언한 연동 계약(ActionTrigger · CaseCard)을 쓰는지 확인.

schema/analysis.py 주석:
- "이 스키마는 기능 2(나의 사건 카드)와 행동 강령 매칭 엔진이 그대로 소비하도록 설계했다"
- ActionTrigger: "행동 강령 매칭 키. 검증된 절차 지식베이스는 이 키로만 조회한다"
"""

from datetime import date

from action_engine import ST, basis_from_triggers, build_card, inf_from_triggers
from action_engine.codes import INF

# ── ActionTrigger 를 1급 입력으로 쓴다 ──────────────────────────────────


def test_트리거만으로도_INF를_판정한다(missing):
    """issues[] 없이 action_triggers[] 만 받아도 판정이 돌아야 한다."""
    triggers = missing["analysis"]["action_triggers"]
    hits = inf_from_triggers(triggers)
    assert hits
    codes = {h.code for h in hits}
    assert INF.RECORD_GAP in codes
    assert INF.RECORD_UNCHECKED in codes
    # 모든 판정에 트리거 키가 근거로 붙는다
    assert all(h.source_trigger_keys for h in hits)


def test_트리거_판정은_issues_판정과_어긋나지_않는다(missing, fraud):
    """같은 입력이면 두 경로가 같은 코드 집합을 내야 한다 (근거 문장만 다르다)."""
    from action_engine import resolve_inf

    for result in (missing, fraud):
        by_trigger = {h.code for h in inf_from_triggers(result["analysis"]["action_triggers"])}
        by_issue = {h.code for h in resolve_inf(result)}
        # issues 경로는 자료 종류로 INF-01* 과 INF-043 을 더 얹으므로 부분집합 관계다
        assert by_trigger <= by_issue, f"트리거 경로에만 있는 코드: {by_trigger - by_issue}"


def test_트리거의_since로_기산일을_채운다(missing):
    """ActionTrigger.since 는 '기한 계산용'으로 선언된 필드다."""
    basis = basis_from_triggers(missing["analysis"]["action_triggers"])
    assert basis.get("decision_time") == date(2022, 3, 15)  # 수사중지 결정일


def test_트리거에_화자가_없으면_동일인번복으로_올리지_않는다(fraud):
    """ActionTrigger 에는 화자 정보가 없다. 모르면 INF-021 로 둔다."""
    codes = {h.code for h in inf_from_triggers(fraud["analysis"]["action_triggers"])}
    assert INF.CONTRADICTION_ACROSS in codes
    assert INF.CONTRADICTION_SELF not in codes


# ── CaseCard 를 소비해 확장한다 ─────────────────────────────────────────


def test_카드가_research_engine_값을_손대지_않고_통과시킨다(missing):
    card = build_card(missing)
    src = missing["analysis"]["case_card"]
    for field in ("case_type", "case_type_label", "requirements_status",
                  "current_stage", "evidence_doc_count", "needs_confirmation_count",
                  "slots_done", "slots_total"):
        assert getattr(card, field) == src[field], f"{field} 가 바뀌었습니다"
    assert card.stages == src["stages"]
    assert card.source_trigger == src["next_trigger"]


def test_카드에_기능2_판정이_붙는다(missing):
    card = build_card(missing)
    assert card.st.code == ST.SUSPENDED_SUSPECT
    assert card.inf
    assert card.tim
    assert card.next_action is not None and card.next_action.why


def test_화면은_카드_하나만_읽으면_된다(missing):
    """research-engine 출력을 따로 뒤지지 않아도 되는지 — 카드에 다 있는가."""
    card = build_card(missing)
    assert card.case_type_label  # 제목
    assert card.stages  # 스테퍼
    assert card.slots_total  # 완료 항목
    assert card.next_action.action  # 다음 행동 조회 키
    assert card.st.reason  # 왜 이 단계인지


def test_절차_문구는_항상_비어있다(missing, fraud):
    """지식베이스가 붙기 전까지 화면은 빈칸을 그린다."""
    for result in (missing, fraud):
        assert build_card(result).procedure is None


def test_검수_전_표시가_카드에_실린다(missing):
    """requirements_status 를 화면이 그대로 보여줄 수 있어야 한다."""
    assert build_card(missing).requirements_status == "draft_unverified"


def test_카드는_JSON으로_직렬화된다(missing):
    """화면이 파일로 받아 읽는 경로."""
    import json

    dumped = build_card(missing).model_dump_json()
    loaded = json.loads(dumped)
    assert loaded["st"]["code"] == ST.SUSPENDED_SUSPECT
    assert loaded["procedure"] is None
