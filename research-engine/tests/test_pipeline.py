"""목업(mockups/research-engine.html)의 중고거래 사기 사례를 끝까지 돌리는 통합 테스트."""

import json

from research_engine.cli import main
from research_engine.pipeline import ResearchPipeline
from research_engine.schema import ClaimSlot, GapCondition, IssueCategory, Stage


def test_documents_classified_and_unreadable_regions_kept(fraud_result):
    types = {d.doc_id: d.doc_type.value for d in fraud_result.documents}
    assert types == {
        "kakao_0601": "messenger", "transfer_receipt": "receipt", "ecrm_receipt": "receipt",
        "memo_handwritten": "memo", "statement": "statement", "note_0602": "user_note",
    }
    unreadable = {(u.doc_id, u.line_no) for d in fraud_result.documents for u in d.unreadable}
    assert unreadable == {("transfer_receipt", 7), ("memo_handwritten", 4)}
    # 읽히지 않은 줄의 OCR 추정 문자열은 어떤 추출 결과에도 쓰이지 않는다
    lines_used = {(c.content.source_doc_id, c.content.source_line) for c in fraud_result.extraction.claims}
    lines_used |= {(e.action.source_doc_id, e.action.source_line) for e in fraud_result.extraction.events}
    assert not lines_used & unreadable


def test_every_output_item_is_traceable_to_a_source(fraud_result):
    for c in fraud_result.extraction.claims:
        assert c.content.source_doc_id and c.content.source_line
    for ev in fraud_result.timeline.events:
        assert ev.sources
    for issue in fraud_result.analysis.issues:
        # 근거 위치가 있거나, '없음' 판단이면 확인한 문서 목록이 있다
        assert issue.sources or issue.checked_doc_ids


def test_timeline_and_case_card(fraud_result):
    tl = fraud_result.timeline
    assert tl.current_stage is Stage.RECEIPT
    transfer = next(e for e in tl.events if e.title == "350,000원 송금")
    assert {s.source_doc_id for s in transfer.sources} == {"transfer_receipt", "kakao_0601"}
    card = fraud_result.analysis.case_card
    assert card.requirements_status == "draft_unverified"
    assert card.evidence_doc_count == 5
    assert card.needs_confirmation_count == len(fraud_result.analysis.issues)


def test_expected_findings(fraud_result):
    issues = fraud_result.analysis.issues
    conflicts = [i for i in issues if i.category is IssueCategory.INCONSISTENCY]
    assert [i.slot for i in conflicts] == [ClaimSlot.TRANSFER_AMOUNT]
    unverified = {i.slot for i in issues if i.condition is GapCondition.CLAIMED_ONLY}
    assert unverified == {ClaimSlot.ACCOUNT_HOLDER, ClaimSlot.SHIPMENT_SENT}  # 목업의 '발송 주장'은 불일치가 아닌 미확인
    missing = {i.slot for i in issues if i.condition is GapCondition.MISSING}
    assert missing == {ClaimSlot.INVESTIGATOR, ClaimSlot.CASE_NUMBER}
    stalled = next(i for i in issues if i.condition is GapCondition.STAGE_STALLED)
    assert stalled.trigger.elapsed_days == 21 and stalled.trigger.stage is Stage.RECEIPT
    assert issues[0].category is IssueCategory.INCONSISTENCY


def test_answering_unreadable_question_reruns_analysis(fraud_result):
    pipeline = ResearchPipeline()
    q = next(q for q in fraud_result.clarifications if q.doc_id == "transfer_receipt")
    after = pipeline.answer(fraud_result, q.request_id, "받는분 메모 중고거래")
    assert not any(u.doc_id == "transfer_receipt" for d in after.documents for u in d.unreadable)
    assert next(x for x in after.clarifications if x.request_id == q.request_id).status == "answered"
    assert not any(i.condition is GapCondition.UNREADABLE and "이체확인증" in i.message for i in after.analysis.issues)
    # 답변이 새 사실을 지어내지 않는다: 예금주는 여전히 미확인
    assert any(i.slot is ClaimSlot.ACCOUNT_HOLDER for i in after.analysis.issues)


def test_cli_run_and_schema(tmp_path, capsys):
    out = tmp_path / "nested" / "result.json"  # 없는 폴더도 만들어 저장한다
    assert main(["run", "tests/fixtures/used_goods_fraud/case.json", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["analysis"]["case_card"]["current_stage"] == "receipt"
    assert "자료끼리 어긋남" in capsys.readouterr().out
    assert main(["schema", "--out-dir", str(tmp_path / "schemas")]) == 0
    schema = json.loads((tmp_path / "schemas" / "action_trigger.schema.json").read_text(encoding="utf-8"))
    assert "key" in schema["properties"]
