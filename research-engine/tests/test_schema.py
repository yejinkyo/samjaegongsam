import pytest
from pydantic import ValidationError

from research_engine.schema import BBox, Sourced, SourceRef, TextLine


def test_sourced_requires_document_and_location():
    with pytest.raises(ValidationError):
        Sourced[str](value="350,000원", source_doc_id="receipt", confidence=0.9)
    with pytest.raises(ValidationError):
        Sourced[str](value="350,000원", source_doc_id="", source_line=3, confidence=0.9)


def test_sourced_confidence_bounds():
    with pytest.raises(ValidationError):
        Sourced[str](value="x", source_doc_id="d", source_line=1, confidence=1.2)


def test_sourced_accepts_line_or_bbox_and_keeps_ref():
    by_line = Sourced[int](value=350000, source_doc_id="receipt", source_line=6, confidence=0.9)
    by_box = Sourced[int](value=350000, source_doc_id="receipt", source_bbox=[10, 20, 200, 60], confidence=0.9)
    assert by_line.ref() == SourceRef(source_doc_id="receipt", source_line=6)
    assert by_box.source_bbox == BBox(x0=10, y0=20, x1=200, y1=60)
    assert by_line.cite() == "receipt · 6줄"


def test_text_line_span_confidence_penalizes_low_confidence_words():
    line = TextLine(doc_id="d", line_no=1, text="받는분 메모 ▒▒", ocr_confidence=0.8, readability=0.8,
                    readable=True, low_confidence_spans=[(7, 9)])
    assert line.span_confidence(0, 3) == 0.8
    assert line.span_confidence(7, 9) == 0.4
    ref = line.ref(0, 3)
    assert ref.quote == "받는분" and ref.source_line == 1


def test_bbox_rejects_inverted_coordinates():
    with pytest.raises(ValidationError):
        BBox(x0=10, y0=10, x1=5, y1=20)
