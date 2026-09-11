from research_engine.ingest import (
    DocumentIngestor,
    KeywordDocClassifier,
    NaiveBayesDocClassifier,
    OcrDocument,
    OcrLine,
    OcrPage,
    OcrWord,
    ReadabilityScorer,
    UserNote,
    apply_clarification,
)
from research_engine.ingest.layout import group_words_into_lines, reading_order
from research_engine.schema import BBox, ClarificationKind, DocumentType, EvidenceLevel, Script


def _word(text, x0, y0, conf=0.95):
    return OcrWord(text=text, bbox=BBox(x0=x0, y0=y0, x1=x0 + 20 * len(text), y1=y0 + 30), confidence=conf)


def test_words_grouped_into_lines_in_reading_order():
    words = [_word("350,000원", 200, 102), _word("이체금액", 20, 100), _word("이체확인증", 20, 20)]
    lines = reading_order(group_words_into_lines(words))
    assert [ln.text for ln in lines] == ["이체확인증", "이체금액 350,000원"]


def test_low_confidence_line_is_marked_unreadable_and_asked_back():
    doc = OcrDocument(
        doc_id="memo",
        file_name="메모.jpg",
        pages=[
            OcrPage(page_no=1, script_hint=Script.HANDWRITTEN, lines=[
                OcrLine(text="6/2 저녁 전화 안받음", bbox=BBox(x0=0, y0=0, x1=300, y1=40), confidence=0.9),
                OcrLine(text="ㅈ ㄷ 겨ㅣ좌 ??", bbox=BBox(x0=0, y0=50, x1=300, y1=90), confidence=0.45),
            ]),
            OcrPage(page_no=2, script_hint=Script.HANDWRITTEN, lines=[
                OcrLine(text="6/3 신고함", bbox=BBox(x0=0, y0=0, x1=300, y1=40), confidence=0.9),
            ]),
        ],
    )
    res = DocumentIngestor().ingest(doc)
    d = res.document
    assert [ln.line_no for ln in d.lines] == [1, 2, 3]  # 페이지를 넘어 줄 번호가 이어진다
    assert d.lines[2].page == 2
    assert [ln.line_no for ln in d.readable_lines()] == [1, 3]
    assert d.unreadable[0].line_no == 2 and d.unreadable[0].bbox == BBox(x0=0, y0=50, x1=300, y1=90)
    q = next(q for q in res.clarifications if q.kind is ClarificationKind.UNREADABLE_TEXT)
    assert q.line_no == 2 and q.context == ["6/2 저녁 전화 안받음", "6/3 신고함"]

    fixed, answered = apply_clarification(d, q, "지갑 잃어버린 날 계좌 확인")
    assert answered.status == "answered"
    line = fixed.line(2)
    assert line.readable and line.origin == "user_clarified" and line.bbox == d.lines[1].bbox
    assert fixed.unreadable == []


def test_cannot_read_answer_keeps_region_unreadable():
    doc = OcrDocument(doc_id="d", file_name="x", pages=[OcrPage(lines=[
        OcrLine(text="판 결", confidence=0.95), OcrLine(text="▒▒▒ ◈", confidence=0.3)])])
    res = DocumentIngestor().ingest(doc)
    q = next(q for q in res.clarifications if q.kind is ClarificationKind.UNREADABLE_TEXT)
    fixed, _ = apply_clarification(res.document, q, "읽을 수 없어요")
    assert not fixed.line(2).readable


def test_word_level_low_confidence_spans():
    line = OcrLine(text="예금주 이*민", confidence=0.8,
                   words=[_word("예금주", 0, 0, 0.95), _word("이*민", 80, 0, 0.3)])
    assert ReadabilityScorer().low_confidence_spans(line) == [(4, 7)]


def test_keyword_classifier_core_types():
    clf = KeywordDocClassifier()
    assert clf.predict(["서울중앙지방법원", "판 결", "사건 2019고단1234 사기", "피 고 인 김○○", "주 문"]).doc_type is DocumentType.JUDGMENT
    assert clf.predict(["진 술 서", "성명: 홍길동", "위 내용은 사실과 다름이 없습니다."]).doc_type is DocumentType.STATEMENT
    assert clf.predict(["영수증", "합계 12,000원", "사업자등록번호 123-45-67890"]).doc_type is DocumentType.RECEIPT
    assert clf.predict(["6/2 전화", "신고함"], handwritten_ratio=1.0).doc_type is DocumentType.MEMO
    unknown = clf.predict(["안녕하세요"])
    assert unknown.doc_type is DocumentType.UNKNOWN and unknown.confidence <= 0.3


def test_unknown_doc_type_triggers_question():
    doc = OcrDocument(doc_id="d", file_name="x", pages=[OcrPage(lines=[OcrLine(text="안녕하세요", confidence=0.95)])])
    res = DocumentIngestor().ingest(doc)
    assert any(q.kind is ClarificationKind.DOCUMENT_TYPE for q in res.clarifications)


def test_naive_bayes_classifier_learns_and_roundtrips(tmp_path):
    samples = [
        ("판결 주문 피고인을 징역 1년에 처한다", DocumentType.JUDGMENT),
        ("피고인 선고 법원 판사 이유", DocumentType.JUDGMENT),
        ("진술서 진술인 위 내용은 사실과 다름이 없습니다", DocumentType.STATEMENT),
        ("진술인 서명 날인 진술서", DocumentType.STATEMENT),
        ("영수증 합계 금액 승인번호", DocumentType.RECEIPT),
        ("합계 결제 금액 영수증 사업자", DocumentType.RECEIPT),
    ]
    clf = NaiveBayesDocClassifier().fit(samples)
    assert clf.predict(["피고인에게 징역을 선고한다"]).doc_type is DocumentType.JUDGMENT
    clf.to_json(tmp_path / "nb.json")
    again = NaiveBayesDocClassifier.from_json(tmp_path / "nb.json")
    assert again.predict(["결제 합계 영수증"]).doc_type is DocumentType.RECEIPT


def test_readability_scorer_fit_separates_good_and_bad_lines():
    good = {"ocr_conf": 0.7, "min_word_conf": 0.6, "garbage_ratio": 0.0, "jamo_ratio": 0.0,
            "handwritten": 1.0, "typewriter": 0.0, "short": 0.0}
    bad = {**good, "ocr_conf": 0.72, "jamo_ratio": 0.3}
    scorer = ReadabilityScorer().fit([(good, 1)] * 20 + [(bad, 0)] * 20)
    assert scorer.score(good) > 0.5 > scorer.score(bad)


def test_user_note_becomes_user_level_document():
    doc = DocumentIngestor.ingest_user_note(UserNote(note_id="n1", text="6월 2일 연락 두절\n\n전화도 안 받음"))
    assert doc.evidence_level is EvidenceLevel.USER
    assert [ln.line_no for ln in doc.lines] == [1, 2]
    assert doc.lines[0].ref().source_doc_id == "n1"


def test_keyword_classifier_notice():
    lines = ["수사중지 결정 통지서", "사건번호 2016형제12345", "결정일자 2022. 3. 15.", "○○경찰서장"]
    assert KeywordDocClassifier().predict(lines).doc_type is DocumentType.NOTICE
