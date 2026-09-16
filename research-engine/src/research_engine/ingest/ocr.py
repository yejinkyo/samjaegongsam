"""OCR 엔진 어댑터.

엔진마다 출력이 다르므로 ``OcrPage``(단어 또는 줄 + bbox + 0~1 신뢰도)로 정규화한다.
- ``load_ocr_document``: 외부 OCR(API·배치) 결과나 라벨링 파일럿 데이터를 JSON으로 읽는다.
- ``TesseractOcrEngine``: 로컬 이미지 OCR. ``pip install research-engine[ocr]`` + Tesseract(kor) 필요.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from ..schema import BBox, DocumentType, Script


class OcrWord(BaseModel):
    text: str
    bbox: BBox
    confidence: float = Field(ge=0.0, le=1.0)


class OcrLine(BaseModel):
    text: str
    bbox: BBox | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    words: list[OcrWord] = Field(default_factory=list)
    script: Script | None = None


class OcrPage(BaseModel):
    page_no: int = Field(default=1, ge=1)
    width: float | None = None
    height: float | None = None
    image_ref: str | None = None
    script_hint: Script = Script.UNKNOWN
    lines: list[OcrLine] = Field(default_factory=list)
    words: list[OcrWord] = Field(default_factory=list, description="줄 정보가 없는 엔진용")


class OcrDocument(BaseModel):
    doc_id: str = Field(min_length=1)
    file_name: str
    captured_at: datetime | None = None
    doc_type_hint: DocumentType | None = Field(default=None, description="사용자가 직접 고른 자료 종류")
    pages: list[OcrPage]


class OcrEngine(Protocol):
    def recognize(self, image_path: Path, page_no: int = 1) -> OcrPage: ...


def load_ocr_document(path: str | Path) -> OcrDocument:
    return OcrDocument.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


class TesseractOcrEngine:
    """pytesseract 기반 OCR. 이 저장소 CI에서는 실행 검증하지 않는다 (바이너리 의존)."""

    def __init__(self, lang: str = "kor+eng", psm: int = 6, preprocess: bool = True, cmd: str | None = None):
        self.lang = lang
        self.psm = psm
        self.preprocess = preprocess
        # 윈도우 설치본은 PATH 에 잡히지 않는 경우가 많아 실행 파일 경로를 따로 받는다
        self.cmd = cmd

    def recognize(self, image_path: Path, page_no: int = 1) -> OcrPage:
        import pytesseract
        from PIL import Image, ImageOps

        if self.cmd:
            pytesseract.pytesseract.tesseract_cmd = self.cmd

        img = ImageOps.exif_transpose(Image.open(image_path))
        if self.preprocess:
            img = preprocess_image(img)
        data = pytesseract.image_to_data(
            img, lang=self.lang, config=f"--psm {self.psm}", output_type=pytesseract.Output.DICT
        )
        grouped: dict[tuple[int, int, int], list[OcrWord]] = {}
        for i, text in enumerate(data["text"]):
            conf = float(data["conf"][i])
            if not text.strip() or conf < 0:
                continue
            x, y, w, h = (data[k][i] for k in ("left", "top", "width", "height"))
            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            grouped.setdefault(key, []).append(
                OcrWord(text=text, bbox=BBox(x0=x, y0=y, x1=x + w, y1=y + h), confidence=conf / 100)
            )
        lines = []
        for words in grouped.values():
            box = words[0].bbox
            for w in words[1:]:
                box = box.union(w.bbox)
            lines.append(
                OcrLine(
                    text=join_words(words),
                    bbox=box,
                    confidence=sum(w.confidence for w in words) / len(words),
                    words=words,
                )
            )
        return OcrPage(
            page_no=page_no, width=img.width, height=img.height, image_ref=str(image_path), lines=lines
        )


def join_words(words: list[OcrWord], space_ratio: float = 0.5) -> str:
    """단어 상자들을 한 줄 문자열로. 띄어쓰기는 상자 사이 간격으로 정한다.

    Tesseract 한국어 모델은 음절 하나하나를 단어로 돌려준다. 공백으로 이어 붙이면
    '사 건 번 호'가 되어 '사건번호' 같은 서식 이름을 찾지 못한다. 간격이 글자 높이의
    ``space_ratio`` 배보다 좁으면 같은 낱말로 붙인다.
    """
    ordered = sorted(words, key=lambda w: w.bbox.x0)
    if not ordered:
        return ""
    heights = sorted(w.bbox.y1 - w.bbox.y0 for w in ordered)
    height = heights[len(heights) // 2] or 1
    out = ordered[0].text
    for prev, cur in zip(ordered, ordered[1:], strict=False):
        gap = cur.bbox.x0 - prev.bbox.x1
        out += ("" if gap < height * space_ratio else " ") + cur.text
    return out


def preprocess_image(img):  # PIL.Image -> PIL.Image
    """저화질 스캔 보정: 흑백, 대비 자동 조정, 잡티 제거, 작은 이미지 확대."""
    from PIL import ImageFilter, ImageOps

    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    if img.width < 1500:
        scale = 1500 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    return img
