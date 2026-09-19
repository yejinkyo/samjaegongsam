"""시연 사건의 '원본' 사진 — 첨부한 자료에서 눌러 볼 수 있게 서류 7장을 그림으로 만든다.

글자는 같은 폴더의 OCR 입력 JSON 에서 그대로 가져온다. 사진과 엔진이 읽은 글자가 어긋나면
'원본 보기'가 오히려 신뢰를 깎는다. 판독 신뢰도가 낮은 줄(▒)은 사진에서도 번져 보이게 그린다.

인물 · 사건 · 기관은 모두 지어낸 것이다. 실제 서류로 쓰이지 않도록 모든 장에 '시연용 가상 자료'를
박고, 기관 직인은 그리지 않는다('직인 생략').

    py 시험자료/시연-실종사건/원본만들기.py        (Pillow · Windows 한글 글꼴 필요)
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
OUT = HERE.parents[1] / "web" / "data" / "demo" / "demo_missing_2017"
FONTS = Path("C:/Windows/Fonts")
W = 1080
MARGIN = 90

# 번진 줄에 원래 적혀 있던 글자 — 사진에는 이 글자를 그리고 그 위를 번지게 한다
SMUDGED = {"▒▒": "없어", "중▒함": "중지함"}

# 표 서식(접수증 · 통지서)에서 '항목 값' 으로 가를 때 쓰는 항목 이름
FORM_LABELS = ["접수번호", "접수일시", "실종자", "신고인", "최종 목격", "접수관서", "사건번호", "피의자", "죄명",
               "결정일자", "결정내용", "이유", "담당 수사관"]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def lines_of(doc_id: str) -> list[dict]:
    d = json.loads((HERE / f"{doc_id}.json").read_text(encoding="utf-8"))
    return [ln for pg in d["pages"] for ln in pg["lines"]]


def restore(text: str) -> tuple[str, bool]:
    """OCR 이 ▒ 로 읽은 줄 → 사진에 그릴 원래 글자, 번지게 할지."""
    smudged = "▒" in text
    for k, v in SMUDGED.items():
        text = text.replace(k, v)
    return text, smudged


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    out, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=f) > width and cur:
            out.append(cur)
            cur = ch.lstrip()
        else:
            cur += ch
    return out + [cur] if cur else out


def paper(height: int, tone=(252, 251, 247)) -> Image.Image:
    img = Image.new("RGB", (W, height), tone)
    # 스캔한 종이 결 — 아주 옅은 얼룩
    rnd = random.Random(height)
    d = ImageDraw.Draw(img)
    for _ in range(1400):
        x, y = rnd.randrange(W), rnd.randrange(height)
        g = rnd.randrange(236, 248)
        d.point((x, y), fill=(g, g, g - 4))
    return img


def label_value(text: str) -> tuple[str, str]:
    for lab in FORM_LABELS:
        if text.startswith(lab + " "):
            return lab, text[len(lab) + 1:]
    return "", text


def smudge(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    """물에 젖은 것처럼 그 칸만 번지게 — 흐림 + 누런 얼룩."""
    region = img.crop(box).filter(ImageFilter.GaussianBlur(4.5))
    img.paste(region, box)
    stain = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(stain)
    x0, y0, x1, y1 = box
    sd.ellipse((x0 - 20, y0 - 18, x1 + 10, y1 + 22), fill=(170, 140, 70, 46))
    img.paste(Image.alpha_composite(img.convert("RGBA"), stain).convert("RGB"))


def form_doc(doc_id: str, title: str, footer: str) -> Image.Image:
    """기관 서식 — 가운데 제목, 항목 | 값 표, 아래 발행 기관(직인 생략)."""
    rows = [restore(ln["text"]) for ln in lines_of(doc_id)[1:]]
    body = [r for r in rows if label_value(r[0])[0]]
    issuer = [r[0] for r in rows if not label_value(r[0])[0]]
    f_title, f_lab, f_val, f_small = font("malgunbd.ttf", 46), font("malgunbd.ttf", 25), font("malgun.ttf", 26), font("malgun.ttf", 20)

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lab_w, pad = 210, 18
    val_w = W - 2 * MARGIN - lab_w - 2 * pad
    heights = [max(1, len(wrap(probe, label_value(t)[1], f_val, val_w))) * 38 + 2 * pad for t, _ in body]
    height = 260 + sum(heights) + (260 + len(issuer) * 40 if issuer else 150)
    img = paper(height)
    d = ImageDraw.Draw(img)

    d.text((W / 2, 110), title, font=f_title, fill=(25, 25, 30), anchor="mm")
    d.line((W / 2 - 150, 150, W / 2 + 150, 150), fill=(25, 25, 30), width=2)

    y = 210
    d.rectangle((MARGIN, y, W - MARGIN, y + sum(heights)), outline=(40, 40, 45), width=2)
    for (text, smudged), hgt in zip(body, heights, strict=True):
        lab, val = label_value(text)
        d.rectangle((MARGIN, y, MARGIN + lab_w, y + hgt), fill=(238, 236, 230), outline=(40, 40, 45), width=1)
        d.line((MARGIN, y + hgt, W - MARGIN, y + hgt), fill=(40, 40, 45), width=1)
        d.text((MARGIN + lab_w / 2, y + hgt / 2), lab, font=f_lab, fill=(30, 30, 35), anchor="mm")
        vy = y + pad
        for part in wrap(d, val, f_val, val_w):
            d.text((MARGIN + lab_w + pad, vy), part, font=f_val, fill=(20, 20, 25))
            vy += 38
        if smudged:
            # 값의 가운데쯤이 번졌다 — 앞뒤 글자는 읽힌다
            x0 = MARGIN + lab_w + pad + int(d.textlength(val[: len(val) // 3], font=f_val))
            smudge(img, (x0, y + 6, x0 + 230, y + hgt - 6))
            d = ImageDraw.Draw(img)
        y += hgt

    y += 70
    for t in issuer:
        if t.startswith("※"):
            for part in wrap(d, t, f_small, W - 2 * MARGIN):
                d.text((MARGIN, y), part, font=f_small, fill=(80, 80, 85))
                y += 30
        else:
            d.text((W / 2, y), t, font=font("malgunbd.ttf", 32), fill=(20, 20, 25), anchor="mm")
            y += 44
    if any(not t.startswith("※") for t in issuer):
        d.text((W / 2 + 190, y - 44), "(직인 생략)", font=f_small, fill=(120, 120, 125), anchor="lm")
    if footer:
        d.text((MARGIN, height - 70), footer, font=f_small, fill=(120, 120, 125))
    return img


def statement(doc_id: str, handwritten: bool) -> Image.Image:
    """진술서 — 줄 친 종이. 손으로 쓴 것은 글자마다 조금씩 흔들리게, 파란 잉크로."""
    raw = lines_of(doc_id)
    title, rest = raw[0]["text"], [restore(ln["text"])[0] for ln in raw[1:]]
    f_title = font("malgunbd.ttf", 44)
    f = font("malgun.ttf", 30 if handwritten else 27)
    step = 58
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    wrapped = []
    for t in rest:
        wrapped += wrap(probe, t, f, W - 2 * MARGIN - 20) or [""]
        if t.startswith("진술") or t.startswith("성명"):
            wrapped.append("")
    height = 240 + (len(wrapped) + 3) * step + 120
    img = paper(height, (250, 250, 246))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 110), title, font=f_title, fill=(25, 25, 30), anchor="mm")
    top = 220
    for i in range(len(wrapped) + 3):
        yy = top + (i + 1) * step
        d.line((MARGIN, yy, W - MARGIN, yy), fill=(196, 205, 222), width=1)

    ink = (28, 52, 128) if handwritten else (22, 22, 28)
    rnd = random.Random(doc_id)
    for i, t in enumerate(wrapped):
        base = top + (i + 1) * step - 12
        x = MARGIN + 10
        if not handwritten:
            d.text((x, base), t, font=f, fill=ink, anchor="ls")
            continue
        for ch in t:
            # 글자마다 조금 들쭉날쭉 — 손글씨처럼 보이게
            glyph = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
            ImageDraw.Draw(glyph).text((10, 48), ch, font=f, fill=ink + (235,), anchor="ls")
            glyph = glyph.rotate(rnd.uniform(-5, 5), resample=Image.BICUBIC)
            img.paste(glyph, (int(x) - 10, int(base - 48 + rnd.uniform(-2.5, 2.5))), glyph)
            x += d.textlength(ch, font=f) + rnd.uniform(-0.6, 1.2)
    return img


def news(doc_id: str) -> Image.Image:
    raw = [ln["text"] for ln in lines_of(doc_id)]
    head, byline, body, tail = raw[0], raw[1], raw[2:-1], raw[-1]
    f_head, f_by, f_body = font("malgunbd.ttf", 44), font("malgun.ttf", 21), font("batang.ttc", 29)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    head_lines = wrap(probe, head, f_head, W - 2 * MARGIN)
    body_lines = [p for t in body for p in wrap(probe, t, f_body, W - 2 * MARGIN) + [""]]
    height = 160 + len(head_lines) * 60 + 80 + len(body_lines) * 46 + 160
    img = paper(height, (246, 242, 230))
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 70), "○○일보  |  사회", font=font("malgunbd.ttf", 22), fill=(150, 40, 40))
    d.line((MARGIN, 108, W - MARGIN, 108), fill=(60, 55, 50), width=3)
    y = 140
    for part in head_lines:
        d.text((MARGIN, y), part, font=f_head, fill=(20, 20, 20))
        y += 60
    d.text((MARGIN, y + 6), byline, font=f_by, fill=(110, 105, 100))
    y += 70
    d.line((MARGIN, y - 18, W - MARGIN, y - 18), fill=(200, 194, 180), width=1)
    for part in body_lines:
        d.text((MARGIN, y), part, font=f_body, fill=(35, 32, 30))
        y += 46
    d.text((MARGIN, y + 20), tail, font=f_by, fill=(140, 135, 128))
    return img


def finish(img: Image.Image, doc_id: str) -> Image.Image:
    """모든 장에 '시연용 가상 자료'를 비스듬히 박고, 사진으로 찍은 것처럼 살짝 기울인다."""
    mark = Image.new("RGBA", img.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    f = font("malgunbd.ttf", 64)
    for y in range(160, img.height, 420):
        md.text((W / 2, y), "시연용 가상 자료", font=f, fill=(200, 60, 60, 38), anchor="mm")
    mark = mark.rotate(18, resample=Image.BICUBIC)
    img = Image.alpha_composite(img.convert("RGBA"), mark).convert("RGB")
    ImageDraw.Draw(img).text((MARGIN, img.height - 40), "※ 타래 시연용으로 지어낸 자료입니다. 실제 인물 · 기관과 관계없습니다.",
                             font=font("malgun.ttf", 18), fill=(150, 150, 155))
    tilt = random.Random(doc_id + "tilt").uniform(-0.8, 0.8)
    return img.rotate(tilt, resample=Image.BICUBIC, expand=True, fillcolor=(214, 212, 206))


DOCS = {
    "missing_report_2017": lambda: form_doc("missing_report_2017", "실종신고 접수증", ""),
    "witness_station_2017": lambda: statement("witness_station_2017", handwritten=False),
    "witness_market_2017": lambda: statement("witness_market_2017", handwritten=True),
    "family_statement_2017": lambda: statement("family_statement_2017", handwritten=True),
    "news_2018": lambda: news("news_2018"),
    "suspension_notice_2019": lambda: form_doc("suspension_notice_2019", "수사결과 통지서", "경찰수사규칙 서식을 본뜬 가상 자료"),
    "tip_statement_2025": lambda: statement("tip_statement_2025", handwritten=True),
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for doc_id, make in DOCS.items():
        finish(make(), doc_id).save(OUT / f"{doc_id}.jpg", quality=84, optimize=True)
    print("원본", len(DOCS), "장을 썼습니다 →", OUT)
