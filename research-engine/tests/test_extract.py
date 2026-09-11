import itertools
from datetime import date, datetime

from research_engine.extract.entities import RuleBasedEntityExtractor
from research_engine.extract.extractor import Extractor
from research_engine.extract.patterns import parse_money, strip_particles
from research_engine.ingest import DocumentIngestor, OcrDocument, OcrLine, OcrPage
from research_engine.schema import ClaimSlot, DocumentType, EntityKind, Polarity, Stage, TextLine


def _line(text, doc_id="d", line_no=1):
    return TextLine(doc_id=doc_id, line_no=line_no, text=text, ocr_confidence=0.95, readability=0.95, readable=True)


def _mentions(text, doc_type=DocumentType.STATEMENT):
    return RuleBasedEntityExtractor().extract_line(_line(text), doc_type, itertools.count(1))


def _doc(doc_id, lines, doc_type):
    ocr = OcrDocument(doc_id=doc_id, file_name=f"{doc_id}.jpg", doc_type_hint=doc_type,
                      pages=[OcrPage(lines=[OcrLine(text=t, confidence=0.95) for t in lines])])
    return DocumentIngestor().ingest(ocr).document


def test_parse_money_korean_units():
    assert parse_money("350,000") == 350000
    assert parse_money("35만") == 350000
    assert parse_money("3만5천") == 35000
    assert parse_money("1억2천만") == 120_000_000


def test_strip_particles_protects_short_names():
    assert strip_particles("김철수는") == "김철수"
    assert strip_particles("홍길동입니") == "홍길동"
    assert strip_particles("이가은") == "이가은"


def test_entities_accounts_orgs_case_numbers_and_roles():
    ms = _mentions("피고인 김철수는 2019고단1234 사건으로 서울중앙지방법원에서 국민 940*-**-****21 계좌 관련 재판을 받았다")
    got = {(m.kind, m.normalized, m.role) for m in ms}
    assert (EntityKind.PERSON, "김철수", "피고인") in got
    assert (EntityKind.CASE_NUMBER, "2019고단1234", None) in got
    assert (EntityKind.ORGANIZATION, "서울중앙지방법원", None) in got
    assert (EntityKind.ACCOUNT, "940*******21", None) in got
    assert (EntityKind.ORGANIZATION, "국민은행", None) in got
    for m in ms:  # 모든 엔티티는 원문 구간을 가리킨다
        assert m.name.quote == m.name.value and m.name.source_line == 1


def test_role_followed_by_common_noun_is_not_a_person():
    assert not [m for m in _mentions("판매자 계좌로 30만원을 송금") if m.kind is EntityKind.PERSON]
    assert _mentions("피해자 이○○은")[0].normalized == "이**"


def test_messenger_speaker_and_account_holder_self_claim():
    doc = _doc("chat", ["2026년 6월 1일 월요일", "[찬찬] [오후 1:50] 국민 940*-**-****21 로 35만원 보내주세요",
                        "[찬찬] [오후 1:52] 계좌는 제 명의예요", "[나] [오후 2:05] 송금했습니다"], DocumentType.MESSENGER)
    res = Extractor().extract([doc], date(2026, 6, 24))
    holder = next(c for c in res.claims if c.slot is ClaimSlot.ACCOUNT_HOLDER)
    assert holder.speaker == "찬찬" and holder.value_is_speaker_self and holder.slot_value == "찬찬"
    assert holder.subject == "940*******21"
    assert holder.said_at.start == datetime(2026, 6, 1, 13, 52)
    account = next(c for c in res.claims if c.slot is ClaimSlot.ACCOUNT_NUMBER)
    assert account.subject == "deposit"
    assert not any(c.slot is ClaimSlot.TRANSFER_AMOUNT for c in res.claims)  # '보내주세요'는 송금 사실이 아니다
    transfer = next(e for e in res.events if e.stage is Stage.TRANSFER)
    assert transfer.time.value.end == datetime(2026, 6, 1, 14, 6)  # 메시지 시각 이전에 일어난 일


def test_record_document_event_uses_labels():
    doc = _doc("receipt", ["이체확인증", "거래일시 2026-06-01 14:05", "입금계좌 940*-**-****21", "이체금액 350,000원"],
               DocumentType.RECEIPT)
    res = Extractor().extract([doc], date(2026, 6, 24))
    [event] = res.events
    assert event.stage is Stage.TRANSFER and event.amount.value == 350000
    assert event.amount.source_line == 4 and event.time.source_line == 2
    assert res.document_dates["receipt"].value.start == datetime(2026, 6, 1, 14, 5)


def test_reported_speech_attributed_to_reported_speaker_and_negation():
    doc = _doc("st", ["진 술 서", "성명: 홍길동", "판매자는 물건을 보냈다고 하였으나 물건을 받지 못하였습니다.", "2026. 6. 5."],
               DocumentType.STATEMENT)
    res = Extractor().extract([doc], date(2026, 6, 24))
    sent = next(c for c in res.claims if c.slot is ClaimSlot.SHIPMENT_SENT)
    received = next(c for c in res.claims if c.slot is ClaimSlot.ITEM_RECEIVED)
    assert sent.speaker == "판매자" and sent.speaker_basis == "reported_speech"
    assert received.speaker == "홍길동" and received.polarity is Polarity.DENY
    assert res.document_dates["st"].source_line == 4


def test_negated_or_requested_actions_are_not_events():
    doc = _doc("st", ["2026년 6월 1일 송금하지 않았습니다", "내일 신고할 예정입니다", "2026년 6월 3일 경찰서에 신고하였다"],
               DocumentType.STATEMENT)
    res = Extractor().extract([doc], date(2026, 6, 24))
    assert [(e.stage, e.action.source_line) for e in res.events] == [(Stage.REPORT, 3)]


def test_typo_date_used_in_record_is_asked_back():
    doc = _doc("rc", ["접수증", "접수일시 2026.13.05 09:12"], DocumentType.RECEIPT)
    res = Extractor().extract([doc], date(2026, 9, 1))
    [q] = res.clarifications
    assert q.line_no == 2 and "2026-03-05" in q.options and q.options[-1] == "모르겠어요"


def test_police_rank_is_not_a_name_and_reporter_byline_is_not_a_person():
    ms = _mentions("담당 수사관 경위 박정호")
    assert [(m.normalized, m.role) for m in ms if m.kind is EntityKind.PERSON] == [("박정호", "담당수사관")]
    assert not [m for m in _mentions("입력 2016.02.03  김○○ 기자", DocumentType.NEWS) if m.kind is EntityKind.PERSON]


def test_notice_document_is_a_record_with_decision_slots():
    doc = _doc("notice", ["수사중지 결정 통지서", "사건번호 2016형제12345", "결정일자 2022. 3. 15.",
                          "결정내용 수사중지(피의자중지)", "담당 수사관 경위 박정호", "○○경찰서장"], DocumentType.NOTICE)
    assert doc.evidence_level.value == "record"
    res = Extractor().extract([doc], date(2026, 9, 11))
    [event] = res.events
    assert event.stage is Stage.OUTCOME and event.time.value.start == datetime(2022, 3, 15)
    slots = {c.slot: c for c in res.claims}
    assert slots[ClaimSlot.DECISION_TIME].subject == "수사중지"
    assert slots[ClaimSlot.INVESTIGATOR].slot_value == "박정호"
    assert slots[ClaimSlot.CASE_NUMBER].speaker == "**경찰서"  # 발급 기관이 화자


def test_petition_request_is_placed_at_document_date_not_the_past_date_in_the_sentence():
    doc = _doc("petition", ["진 정 서", "진정인 이순자", "2015. 10. 10. 실종된 아들 김민수 사건의 재수사를 요청합니다.", "2023. 4. 2."],
               DocumentType.COMPLAINT)
    res = Extractor().extract([doc], date(2026, 9, 11))
    petition = next(e for e in res.events if e.action_kind == "petition")
    assert petition.stage is Stage.REPORT and petition.time.value.start == datetime(2023, 4, 2)
    assert petition.time.source_line == 4


def test_last_seen_claim_from_reported_speech():
    doc = _doc("news", ["입력 2016.02.03 09:10", "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다."],
               DocumentType.NEWS)
    res = Extractor().extract([doc], date(2026, 9, 11))
    seen = next(c for c in res.claims if c.slot is ClaimSlot.LAST_SEEN_TIME)
    assert seen.speaker == "경찰" and seen.speaker_basis == "reported_speech"
    assert seen.slot_time.start == datetime(2015, 10, 10, 22)  # '지난해'(연 단위)보다 구체적인 시각을 쓴다


def test_investigator_change_and_new_investigator_claims():
    doc = _doc("memo", ["15년 10월 10일 밤 연락 끊김", "작년 추석 무렵 수사관한테 전화 → 담당자 바뀌었다고 함", "새 담당 형사 이름 김영수"],
               DocumentType.MEMO)
    res = Extractor().extract([doc], date(2026, 9, 11))
    change = next(c for c in res.claims if c.slot is ClaimSlot.INVESTIGATOR_CHANGE)
    assert change.content.source_line == 2 and change.slot_time is not None
    new = next(c for c in res.claims if c.slot is ClaimSlot.INVESTIGATOR)
    assert new.slot_value == "김영수" and new.content.source_line == 3
    assert not any(c.slot is ClaimSlot.INVESTIGATOR_CHANGE for c in _doc_claims("담당 형사가 바뀌지 않았다"))


def _doc_claims(text):
    return Extractor().extract([_doc("x", [text], DocumentType.MEMO)], date(2026, 9, 11)).claims
