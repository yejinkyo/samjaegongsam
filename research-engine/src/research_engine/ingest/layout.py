"""레이아웃: 단어 → 줄 묶기와 읽기 순서 정렬."""

from __future__ import annotations

from .ocr import OcrLine, OcrWord


def group_words_into_lines(words: list[OcrWord], min_overlap: float = 0.5) -> list[OcrLine]:
    """세로로 충분히 겹치는 단어를 같은 줄로 묶는다."""
    rows: list[list[OcrWord]] = []
    for word in sorted(words, key=lambda w: (w.bbox.center_y, w.bbox.x0)):
        for row in rows:
            if row[-1].bbox.vertical_overlap(word.bbox) >= min_overlap:
                row.append(word)
                break
        else:
            rows.append([word])

    lines = []
    for row in rows:
        row.sort(key=lambda w: w.bbox.x0)
        box = row[0].bbox
        for w in row[1:]:
            box = box.union(w.bbox)
        lines.append(
            OcrLine(
                text=" ".join(w.text for w in row),
                bbox=box,
                confidence=sum(w.confidence for w in row) / len(row),
                words=row,
            )
        )
    return lines


def reading_order(lines: list[OcrLine], min_overlap: float = 0.5) -> list[OcrLine]:
    """위→아래, 같은 높이면 왼쪽→오른쪽. bbox가 없는 줄은 입력 순서를 유지한다."""
    if any(ln.bbox is None for ln in lines):
        return list(lines)
    ordered = sorted(lines, key=lambda ln: ln.bbox.y0)  # type: ignore[union-attr]
    rows: list[list[OcrLine]] = []
    for ln in ordered:
        if rows and rows[-1][0].bbox.vertical_overlap(ln.bbox) >= min_overlap:  # type: ignore[union-attr,arg-type]
            rows[-1].append(ln)
        else:
            rows.append([ln])
    return [ln for row in rows for ln in sorted(row, key=lambda x: x.bbox.x0)]  # type: ignore[union-attr]
