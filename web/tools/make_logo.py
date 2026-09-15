"""손으로 그린 로고를 화면용 PNG 두 개로 바꾼다.

원본(`web/assets/logo-original.png`)은 흰 종이에 검게 그린 그림이다.

    바깥 흰 배경만 투명하게  →  검은 부분에 색을 올린다
    (원 안쪽 흰 줄무늬는 그림의 일부라 그대로 흰색으로 남긴다)

    py web/tools/make_logo.py

Pillow 가 필요하다. 없으면 ``py -m pip install --user pillow``.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parents[1] / "assets"
SRC = ASSETS / "logo-original.png"

DEEP = (74, 46, 160)      # #4A2EA0 — 밝은 화면용
LIGHT = (198, 177, 240)   # #C6B1F0 — 어두운 화면에서 읽히는 밝기
SIZE = 256
WHITE_ENOUGH = 200        # 이보다 밝으면 '배경 후보'


def _lum(p: tuple[int, int, int]) -> int:
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def _outside_mask(img: Image.Image) -> bytearray:
    """테두리에서 시작해 밝은 픽셀만 타고 번진다 — 안쪽 흰 줄무늬는 닿지 않는다."""
    w, h = img.size
    px = img.load()
    mask = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        if not mask[y * w + x] and _lum(px[x, y]) > WHITE_ENOUGH:
            mask[y * w + x] = 1
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                seed(nx, ny)
    return mask


def tint(img: Image.Image, mask: bytearray, color: tuple[int, int, int]) -> Image.Image:
    w, h = img.size
    px = img.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        row = y * w
        for x in range(w):
            if mask[row + x]:
                continue
            t = 1 - _lum(px[x, y]) / 255          # 검을수록 1, 흰 줄무늬는 0
            op[x, y] = (
                round(255 + (color[0] - 255) * t),
                round(255 + (color[1] - 255) * t),
                round(255 + (color[2] - 255) * t),
                255,
            )

    box = out.getbbox()
    out = out.crop(box)
    side = max(out.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(out, ((side - out.size[0]) // 2, (side - out.size[1]) // 2))
    return square.resize((SIZE, SIZE), Image.LANCZOS)


def main() -> None:
    src = Image.open(SRC).convert("RGB")
    mask = _outside_mask(src)
    for name, color in (("logo.png", DEEP), ("logo-light.png", LIGHT)):
        tint(src, mask, color).save(ASSETS / name)
        print(f"{name}: {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
