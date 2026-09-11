"""한국어 시간 표현 정규화.

실제 자료는 어수선하다 — 이 모듈이 추출 정확도 병목이 될 가능성이 크므로 규칙을 명시적으로 둔다.

지원 범위
- 절대 날짜: 2026년 6월 1일 / 2026.6.1. / 2026-06-01 / '23.03.05 / 단기 4290년 …
- 부분 날짜: 6월 1일, 6/1, 6월 (연도는 기준일에서 과거 쪽으로 추정)
- 시각: 오후 2:05, 14:05, 오후 3시 20분경, 저녁 (앞 날짜에 붙임)
- 상대 날짜
    · 발화 기준(deictic): 오늘, 어제, 그저께, 지난주 금요일, 지난달, 작년, 3일 전 …
      → 발화 시점(메신저 날짜 줄 / 문서 작성일 / 촬영일) 기준
    · 문맥 기준(anaphoric): 그날, 다음날, 전날, 이튿날, 3일 후 …
      → 직전에 언급된 날짜 기준 (없으면 발화 기준 + 확인 필요)
- 음력: 음력 8월 15일, 윤2월 10일, 8월 15일(음) → 양력 변환
- 오탈자·OCR 혼동: 2O26 → 2026 (확인 필요), 달력에 없는 날짜·요일 불일치 → 교정 후보만 제시

원칙: 교정은 '후보'로만 두고 확정하지 않는다. 후보가 여러 개면 start/end를 비워 둔다.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from korean_lunar_calendar import KoreanLunarCalendar

from ..schema import TimeCandidate, TimeGranularity, TimeKind, TimeValue

G = TimeGranularity
K = TimeKind

WEEKDAYS = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}

# 기준일 출처별 신뢰 가중치
ANCHOR_FACTOR = {
    "message_date": 0.95,
    "document_date": 0.9,
    "mentioned_date": 0.85,
    "capture_date": 0.6,
    "as_of": 0.5,
}
WEAK_ANCHORS = {"capture_date", "as_of"}


@dataclass(frozen=True)
class Anchor:
    day: date
    source: str


@dataclass
class TimeMatch:
    start: int
    end: int
    value: TimeValue
    confidence: float
    day: date | None = None  # 시각을 붙일 수 있는 단일 날짜
    is_clock: bool = False


# ── 정규식 ──────────────────────────────────────────────────────────────

_D = r"[0-9OoIl|]"
_APPROX = r"(?P<approx>\s*(?:경|쯤|무렵|초순|중순|하순|초|말))?"

FULL_DATE = re.compile(
    r"(?<![0-9A-Za-z])"
    r"(?P<lunar>음력\s*|\(음\)\s*)?"
    r"(?:(?P<era>단기|서기)\s*)?"
    rf"(?P<apos>')?(?P<y>{_D}{{4}}|\d{{2}})\s*(?P<s1>년|\.|-|/)\s*"
    rf"(?P<leap>윤\s*)?(?P<m>{_D}{{1,2}})\s*(?P<s2>월|\.|-|/)\s*"
    rf"(?P<d>{_D}{{1,2}})(?![0-9])(?:\s*일|\.(?!\d))?"
    r"(?:\s*\((?P<wd>[월화수목금토일])(?:요일)?\)|\s+(?P<wd2>[월화수목금토일])요일)?"
    r"(?P<lunar2>\s*\(음(?:력)?\))?" + _APPROX
)
YEAR_MONTH = re.compile(
    r"(?<![0-9])(?:(?P<era>단기|서기)\s*)?(?P<y>\d{4})\s*년\s*(?P<m>\d{1,2})\s*월(?!\s*\d)" + _APPROX
)
YEAR_ONLY = re.compile(r"(?<![0-9])(?:(?P<era>단기|서기)\s*)?(?P<y>\d{4})\s*년(?!\s*\d)" + _APPROX)
MONTH_DAY = re.compile(
    r"(?<![0-9.\-/])(?P<lunar>음력\s*)?(?P<leap>윤\s*)?(?P<m>\d{1,2})\s*월\s*(?P<d>\d{1,2})\s*일"
    r"(?:\s*\((?P<wd>[월화수목금토일])(?:요일)?\))?(?P<lunar2>\s*\(음(?:력)?\))?" + _APPROX
)
SLASH_MD = re.compile(
    r"(?<![0-9/.\-])(?P<m>\d{1,2})/(?P<d>\d{1,2})(?![0-9/])(?!\s*(?:이상|이하|정도|분량|지분|확률))"
)
MONTH_ONLY = re.compile(r"(?<![0-9.\-/])(?P<m>\d{1,2})\s*월(?!\s*\d)(?![가-힣]*요일)" + _APPROX)

CLOCK = re.compile(
    r"(?<![0-9:])(?:(?P<ampm>오전|오후|새벽|아침|저녁|밤|낮|AM|PM|am|pm)\s*)?"
    r"(?P<h>\d{1,2})\s*:\s*(?P<mi>\d{2})(?::\d{2})?(?![0-9:])"
)
KO_TIME = re.compile(
    r"(?<![0-9])(?:(?P<ampm>오전|오후|새벽|아침|저녁|밤|낮)\s*)?"
    r"(?P<h>\d{1,2})\s*시(?![간각작])(?:\s*(?P<mi>\d{1,2})\s*분|\s*(?P<half>반))?"
    r"(?P<approx>\s*(?:경|쯤|무렵))?"
)
DAYPART = re.compile(r"(?P<part>새벽|아침|오전|점심|낮|오후|저녁|밤)(?!\s*\d)")
DAYPART_HOURS = {
    "새벽": (0, 6), "아침": (6, 10), "오전": (6, 12), "점심": (11, 14),
    "낮": (11, 16), "오후": (12, 18), "저녁": (17, 22), "밤": (20, 24),
}

DEICTIC_DAY = {"오늘": 0, "금일": 0, "어제": -1, "어저께": -1, "작일": -1, "그저께": -2, "그제": -2,
               "내일": 1, "명일": 1, "모레": 2}
ANAPHORIC_DAY = {"그날": 0, "당일": 0, "같은날": 0, "전날": -1, "전일": -1, "다음날": 1, "이튿날": 1, "익일": 1}
DAY_WORD = re.compile(
    r"(?<![가-힣])(?P<w>오늘(?!날)|금일|어저께|어제|작일|그저께|그제(?!서야|야)|내일|명일|모레|그날|당일|같은\s*날|전날|전일|"
    r"다음\s*날|이튿날|익일)"
)
VAGUE_DAYS = re.compile(r"(?P<w>엊그제|엊그저께|며칠\s*(?:전|前))")
NUM_WORDS = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}
NATIVE_DAYS = {"하루": 1, "이틀": 2, "사흘": 3, "나흘": 4, "닷새": 5, "엿새": 6, "이레": 7, "여드레": 8,
               "아흐레": 9, "열흘": 10, "보름": 15, "일주일": 7, "이주일": 14}
N_UNIT = re.compile(
    r"(?<![0-9가-힣])(?P<n>\d+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s*"
    r"(?P<unit>일|주일|주|개월|달|년|해)\s*(?P<dir>전|前|후|뒤|만에)"
)
NATIVE = re.compile(r"(?P<w>" + "|".join(sorted(NATIVE_DAYS, key=len, reverse=True)) + r")\s*(?P<dir>전|前|후|뒤|만에)")
WEEK_REL = re.compile(
    r"(?P<rel>지지난|지난|저번|이번|다음|다다음)\s*(?P<unit>주말|주)(?!\s*\d)(?:\s*(?P<wd>[월화수목금토일])요일)?"
)
WEEKDAY_ALONE = re.compile(r"(?<![주매])(?:(?P<rel>지난|이번|다음)\s*)?(?P<wd>[월화수목금토일])요일")
MONTH_REL = re.compile(r"(?P<rel>지지난|지난|저번|이번|다음|다다음)\s*달")
MONTH_REL_NAMED = re.compile(r"(?P<rel>지난|작년|올해|내년)\s*(?P<m>\d{1,2})\s*월(?!\s*\d)")
YEAR_REL = re.compile(r"(?P<w>재작년|작년|지난\s*해|올해|금년|내년|다음\s*해|이듬해)")

_OCR_DIGIT = str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1", "|": "1"})
_CONFUSABLE = {"0": "689", "1": "74", "2": "7", "3": "85", "4": "19", "5": "63",
               "6": "508", "7": "12", "8": "306", "9": "04"}


# ── 날짜 유틸 ───────────────────────────────────────────────────────────


def _valid(y: int, m: int, d: int) -> bool:
    return 1 <= m <= 12 and 1 <= d <= calendar.monthrange(y, m)[1] if 1 <= y <= 9999 else False


def _day_iv(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time())
    return start, start + timedelta(days=1)


def _month_iv(y: int, m: int) -> tuple[datetime, datetime]:
    start = datetime(y, m, 1)
    return start, datetime(y + (m == 12), m % 12 + 1, 1)


def _year_iv(y: int) -> tuple[datetime, datetime]:
    return datetime(y, 1, 1), datetime(y + 1, 1, 1)


def _add_months(d: date, n: int) -> tuple[int, int]:
    idx = d.year * 12 + (d.month - 1) + n
    return idx // 12, idx % 12 + 1


def _monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def lunar_to_solar(y: int, m: int, d: int, leap: bool = False) -> date | None:
    cal = KoreanLunarCalendar()
    if not cal.setLunarDate(y, m, d, leap):
        return None
    return date(cal.solarYear, cal.solarMonth, cal.solarDay)


def _narrow_month(start: datetime, end: datetime, approx: str | None) -> tuple[datetime, datetime, bool]:
    """'초순/중순/하순/초/말' 로 월 구간을 좁히고, '경/쯤'이면 넓힌다."""
    a = (approx or "").strip()
    if a in ("초", "초순"):
        return start, start + timedelta(days=10), True
    if a == "중순":
        return start + timedelta(days=10), start + timedelta(days=20), True
    if a in ("말", "하순"):
        return start + timedelta(days=20), end, True
    if a in ("경", "쯤", "무렵"):
        return start - timedelta(days=15), end + timedelta(days=15), True
    return start, end, False


class TemporalNormalizer:
    def __init__(self, today: date | None = None):
        self.today = today or date.today()

    # ── 공개 API ──

    def extract(self, text: str, deictic: Anchor, anaphoric: Anchor | None = None) -> list[TimeMatch]:
        dates = self._select(
            self._full_dates(text)
            + self._year_month(text)
            + self._year_only(text)
            + self._month_day(text, deictic)
            + self._slash_md(text, deictic)
            + self._month_only(text, deictic)
            + self._relative(text, deictic, anaphoric)
        )
        clocks = [
            c for c in self._select(self._clocks(text) + self._dayparts(text))
            if not any(c.start < d.end and d.start < c.end for d in dates)
        ]
        return self._attach_clocks(text, dates, clocks, deictic)

    def is_date_line(self, text: str) -> TimeMatch | None:
        """줄 전체가 날짜 하나인가 (메신저 날짜 구분선 등)."""
        stripped = text.strip()
        for m in self._full_dates(stripped):
            rest = (stripped[: m.start] + stripped[m.end :]).strip(" -—=·[]()")
            if not rest or re.fullmatch(r"[월화수목금토일]요일", rest):
                return m if m.day is not None and not m.value.needs_confirmation else None
        return None

    # ── 선택·결합 ──

    @staticmethod
    def _select(cands: list[TimeMatch]) -> list[TimeMatch]:
        kept: list[TimeMatch] = []
        for c in sorted(cands, key=lambda c: (-(c.end - c.start), c.start)):
            if not any(c.start < k.end and k.start < c.end for k in kept):
                kept.append(c)
        return sorted(kept, key=lambda c: c.start)

    def _attach_clocks(
        self, text: str, dates: list[TimeMatch], clocks: list[TimeMatch], deictic: Anchor
    ) -> list[TimeMatch]:
        out = list(dates)
        joiner = re.compile(r"[\s,()\[\]월화수목금토일요]{0,8}")
        for c in clocks:
            host = None
            for d in dates:
                before = d.end <= c.start and joiner.fullmatch(text[d.end : c.start])
                after = c.end <= d.start and joiner.fullmatch(text[c.end : d.start])
                if before or after:
                    host = d
            if host is not None and (host.day is not None or host.value.candidates):
                merged = self._with_clock(host, c)
                out[out.index(host)] = merged
                dates = [merged if d is host else d for d in dates]
            elif c.value.note != "daypart":
                out.append(self._contextual_clock(c, deictic))
        return sorted(out, key=lambda m: m.start)

    def _with_clock(self, host: TimeMatch, clock: TimeMatch) -> TimeMatch:
        cv, hv = clock.value, host.value
        offset_s, offset_e = cv.start - datetime(2000, 1, 1), cv.end - datetime(2000, 1, 1)  # type: ignore[operator]

        def shift(day: date) -> tuple[datetime, datetime]:
            base = datetime.combine(day, time())
            return base + offset_s, base + offset_e

        cands = []
        if host.day is not None:
            start, end = shift(host.day)
            if hv.approximate and not cv.approximate:
                start, end = start - timedelta(hours=1), end + timedelta(hours=1)
            for alt in cv.candidates:  # 오전/오후 모호
                cands.append(
                    TimeCandidate(
                        start=datetime.combine(host.day, time()) + (alt.start - datetime(2000, 1, 1)),
                        end=datetime.combine(host.day, time()) + (alt.end - datetime(2000, 1, 1)),
                        reason=alt.reason,
                    )
                )
        else:
            start = end = None
        for hc in hv.candidates:
            s, e = shift(hc.start.date())
            cands.append(TimeCandidate(start=s, end=e, reason=hc.reason))
        value = hv.model_copy(
            update={
                "raw": f"{hv.raw} {cv.raw}",
                "start": start,
                "end": end,
                "granularity": cv.granularity,
                "approximate": hv.approximate or cv.approximate,
                "candidates": cands,
            }
        )
        return TimeMatch(
            start=min(host.start, clock.start),
            end=max(host.end, clock.end),
            value=value,
            confidence=min(host.confidence, clock.confidence + 0.05),
            day=host.day,
        )

    def _contextual_clock(self, clock: TimeMatch, anchor: Anchor) -> TimeMatch:
        host = TimeMatch(
            start=clock.start,
            end=clock.start,
            value=TimeValue(
                raw="",
                kind=K.CONTEXTUAL,
                anchor=anchor.day,
                anchor_source=anchor.source,
                needs_confirmation=anchor.source in WEAK_ANCHORS,
                note="날짜는 앞선 날짜 표시(또는 문서 기준일)에서 가져옴",
            ),
            confidence=0.85 * ANCHOR_FACTOR.get(anchor.source, 0.5),
            day=anchor.day,
        )
        merged = self._with_clock(host, clock)
        merged.value.raw = clock.value.raw
        return merged

    # ── 절대/부분 날짜 ──

    def _full_dates(self, text: str) -> list[TimeMatch]:
        out = []
        for m in FULL_DATE.finditer(text):
            s1, s2 = m["s1"], m["s2"]
            if (s1 == "년") != (s2 == "월") or (s1 != "년" and s1 != s2):
                continue
            y_s, m_s, d_s = m["y"], m["m"], m["d"]
            if len(y_s) == 2 and not (s1 == "년" or m["apos"] or (len(m_s) == 2 and len(d_s) == 2)):
                continue
            raw_digits = y_s + m_s + d_s
            n_digits = sum(ch.isdigit() for ch in raw_digits)
            if n_digits < len(raw_digits) - 1:  # 글자 혼동은 1자까지만 허용
                continue
            y_s, m_s, d_s = (p.translate(_OCR_DIGIT) for p in (y_s, m_s, d_s))
            y = int(y_s)
            if len(y_s) == 2:
                y += 2000 if y <= self.today.year % 100 + 1 else 1900
            if m["era"] == "단기":
                y -= 2333
            value, conf, day = self._resolve_ymd(
                raw=m.group(0).strip(),
                y=y, mo=int(m_s), d=int(d_s),
                digits=(str(y), m_s, d_s),
                lunar=bool(m["lunar"] or m["lunar2"]),
                leap=bool(m["leap"]),
                weekday=m["wd"] or m["wd2"],
                ocr_fixed=n_digits != len(raw_digits),
                approx=m["approx"],
            )
            out.append(TimeMatch(m.start(), m.end(), value, conf, day))
        return out

    def _resolve_ymd(
        self,
        raw: str,
        y: int,
        mo: int,
        d: int,
        digits: tuple[str, str, str],
        lunar: bool = False,
        leap: bool = False,
        weekday: str | None = None,
        ocr_fixed: bool = False,
        approx: str | None = None,
        kind: TimeKind = K.ABSOLUTE,
        base_conf: float = 0.95,
        anchor: Anchor | None = None,
    ) -> tuple[TimeValue, float, date | None]:
        note = None
        day: date | None = None
        in_range = 1900 <= y <= self.today.year + 5
        if lunar:
            day = lunar_to_solar(y, mo, d, leap) if in_range else None
            if day is None:
                return self._unresolved(raw, "음력 달력에 없는 날짜입니다", anchor), 0.15, None
            kind, note = K.LUNAR, f"음력 {y}.{mo}.{d}{' (윤달)' if leap else ''} → 양력 변환"
            base_conf = min(base_conf, 0.85)
        elif in_range and _valid(y, mo, d):
            day = date(y, mo, d)

        common = {"raw": raw, "anchor": anchor.day if anchor else None,
                  "anchor_source": anchor.source if anchor else None}

        if day is None:
            cands = self._typo_candidates(digits, weekday)
            start, end = (cands[0].start, cands[0].end) if len(cands) == 1 else (None, None)
            value = TimeValue(
                **common, start=start, end=end, granularity=G.DAY, kind=K.CORRECTED,
                candidates=cands if len(cands) > 1 else [], needs_confirmation=True,
                note=f"달력에 없는 날짜입니다 ({y}.{mo}.{d}) — 교정 후보 {len(cands)}개",
            )
            return value, 0.35 if len(cands) == 1 else 0.15, None

        if weekday is not None and WEEKDAYS[weekday] != day.weekday():
            cands = [TimeCandidate(start=_day_iv(day)[0], end=_day_iv(day)[1], reason="적힌 날짜 그대로 (요일 오기)")]
            cands += [c for c in self._typo_candidates(digits, weekday) if c.start.date() != day]
            value = TimeValue(
                **common, granularity=G.DAY, kind=K.CORRECTED, candidates=cands, needs_confirmation=True,
                note=f"적힌 요일({weekday})과 날짜가 맞지 않습니다",
            )
            return value, 0.2, None

        start, end = _day_iv(day)
        approximate = False
        if approx and approx.strip() in ("경", "쯤", "무렵"):
            start, end, approximate = start - timedelta(days=2), end + timedelta(days=2), True
        needs = False
        conf = base_conf
        if ocr_fixed:
            kind, needs, conf = K.CORRECTED, True, 0.5
            note = "OCR 글자 혼동(O→0, l→1 등)을 숫자로 바꿔 읽었습니다"
        if anchor is not None and anchor.source in WEAK_ANCHORS and kind in (K.PARTIAL, K.LUNAR):
            needs = True
        value = TimeValue(
            **common, start=start, end=end, granularity=G.DAY, kind=kind,
            approximate=approximate, needs_confirmation=needs, note=note,
        )
        return value, conf, day

    def _typo_candidates(self, digits: tuple[str, str, str], weekday: str | None, limit: int = 5) -> list[TimeCandidate]:
        y_s, m_s, d_s = digits
        found: dict[date, str] = {}

        def consider(ys: str, ms: str, ds: str, reason: str) -> None:
            try:
                y, mo, d = int(ys), int(ms), int(ds)
            except ValueError:
                return
            if not (1900 <= y <= self.today.year + 1 and _valid(y, mo, d)):
                return
            day = date(y, mo, d)
            if weekday is not None and day.weekday() != WEEKDAYS[weekday]:
                return
            found.setdefault(day, reason)

        consider(y_s, d_s, m_s, "월·일 순서 바뀜")
        for label, idx in (("연", 0), ("월", 1), ("일", 2)):
            part = digits[idx]
            for i, ch in enumerate(part):
                for alt in _CONFUSABLE.get(ch, ""):
                    new = part[:i] + alt + part[i + 1 :]
                    parts = list(digits)
                    parts[idx] = new
                    consider(*parts, f"{label} 숫자 혼동 ({ch}→{alt})")
            if idx > 0 and len(part) == 2:
                for keep in part:
                    parts = list(digits)
                    parts[idx] = keep
                    consider(*parts, f"{label} 숫자 한 자리 잘못 들어감")
        for i in range(len(y_s) - 1):
            swapped = y_s[:i] + y_s[i + 1] + y_s[i] + y_s[i + 2 :]
            consider(swapped, m_s, d_s, "연도 숫자 순서 바뀜")
        return [
            TimeCandidate(start=_day_iv(d)[0], end=_day_iv(d)[1], reason=r)
            for d, r in list(found.items())[:limit]
        ]

    @staticmethod
    def _unresolved(raw: str, note: str, anchor: Anchor | None = None) -> TimeValue:
        return TimeValue(
            raw=raw, kind=K.UNRESOLVED, needs_confirmation=True, note=note,
            anchor=anchor.day if anchor else None, anchor_source=anchor.source if anchor else None,
        )

    def _year_month(self, text: str) -> list[TimeMatch]:
        out = []
        for m in YEAR_MONTH.finditer(text):
            y, mo = int(m["y"]) - (2333 if m["era"] == "단기" else 0), int(m["m"])
            raw = m.group(0).strip()
            if not (1 <= mo <= 12 and 1900 <= y <= self.today.year + 5):
                out.append(TimeMatch(m.start(), m.end(), self._unresolved(raw, "달력에 없는 연·월입니다"), 0.15))
                continue
            start, end, approx = _narrow_month(*_month_iv(y, mo), m["approx"])
            value = TimeValue(raw=raw, start=start, end=end, granularity=G.MONTH, approximate=approx)
            out.append(TimeMatch(m.start(), m.end(), value, 0.9))
        return out

    def _year_only(self, text: str) -> list[TimeMatch]:
        out = []
        for m in YEAR_ONLY.finditer(text):
            y = int(m["y"]) - (2333 if m["era"] == "단기" else 0)
            if not 1900 <= y <= self.today.year + 5:
                continue
            start, end = _year_iv(y)
            a = (m["approx"] or "").strip()
            approx = bool(a)
            if a in ("경", "쯤", "무렵"):
                start, end = datetime(y - 1, 7, 1), datetime(y + 1, 7, 1)
            elif a in ("초", "초순"):
                end = datetime(y, 4, 1)
            elif a in ("말", "하순"):
                start = datetime(y, 10, 1)
            value = TimeValue(raw=m.group(0).strip(), start=start, end=end, granularity=G.YEAR, approximate=approx)
            out.append(TimeMatch(m.start(), m.end(), value, 0.9))
        return out

    def _infer_year(self, mo: int, d: int, anchor: Anchor) -> int:
        """연도 없는 날짜: 기준일 이후 31일을 넘으면 작년으로 본다 (자료는 대개 과거를 서술)."""
        y = anchor.day.year
        dd = min(d, calendar.monthrange(y, mo)[1]) if 1 <= mo <= 12 else 1
        if 1 <= mo <= 12 and date(y, mo, dd) > anchor.day + timedelta(days=31):
            y -= 1
        return y

    def _month_day(self, text: str, anchor: Anchor, pattern: re.Pattern[str] = MONTH_DAY, factor: float = 1.0) -> list[TimeMatch]:
        out = []
        for m in pattern.finditer(text):
            mo, d = int(m["m"]), int(m["d"])
            if pattern is SLASH_MD and not (1 <= mo <= 12 and 1 <= d <= 31):
                continue
            y = self._infer_year(mo, d, anchor)
            groups = m.groupdict()
            value, conf, day = self._resolve_ymd(
                raw=m.group(0).strip(), y=y, mo=mo, d=d, digits=(str(y), m["m"], m["d"]),
                lunar=bool(groups.get("lunar") or groups.get("lunar2")), leap=bool(groups.get("leap")),
                weekday=groups.get("wd"), approx=groups.get("approx"),
                kind=K.PARTIAL, base_conf=0.85 * ANCHOR_FACTOR.get(anchor.source, 0.5) * factor, anchor=anchor,
            )
            if value.kind is K.PARTIAL:
                value.note = f"연도는 기준일({anchor.day.isoformat()})에서 추정"
            out.append(TimeMatch(m.start(), m.end(), value, conf, day))
        return out

    def _slash_md(self, text: str, anchor: Anchor) -> list[TimeMatch]:
        return self._month_day(text, anchor, SLASH_MD, factor=0.85)

    def _month_only(self, text: str, anchor: Anchor) -> list[TimeMatch]:
        out = []
        for m in MONTH_ONLY.finditer(text):
            mo = int(m["m"])
            if not 1 <= mo <= 12:
                continue
            y = self._infer_year(mo, 1, anchor)
            start, end, approx = _narrow_month(*_month_iv(y, mo), m["approx"])
            value = TimeValue(
                raw=m.group(0).strip(), start=start, end=end, granularity=G.MONTH, kind=K.PARTIAL,
                approximate=approx, anchor=anchor.day, anchor_source=anchor.source,
                needs_confirmation=anchor.source in WEAK_ANCHORS,
                note=f"연도는 기준일({anchor.day.isoformat()})에서 추정",
            )
            out.append(TimeMatch(m.start(), m.end(), value, 0.7 * ANCHOR_FACTOR.get(anchor.source, 0.5)))
        return out

    # ── 상대 날짜 ──

    def _rel(
        self,
        m: re.Match[str],
        anchor: Anchor,
        start: datetime,
        end: datetime,
        granularity: TimeGranularity,
        day: date | None = None,
        fallback: bool = False,
        vague: bool = False,
    ) -> TimeMatch:
        needs = anchor.source in WEAK_ANCHORS or fallback or vague
        note = "문맥상 기준 날짜가 없어 발화 시점 기준으로 계산" if fallback else None
        value = TimeValue(
            raw=m.group(0).strip(), start=start, end=end, granularity=granularity, kind=K.RELATIVE,
            approximate=vague, anchor=anchor.day, anchor_source=anchor.source, needs_confirmation=needs, note=note,
        )
        conf = 0.85 * ANCHOR_FACTOR.get(anchor.source, 0.5) * (0.6 if fallback or vague else 1.0)
        return TimeMatch(m.start(), m.end(), value, conf, day)

    def _relative(self, text: str, deictic: Anchor, anaphoric: Anchor | None) -> list[TimeMatch]:
        out: list[TimeMatch] = []
        a = deictic.day

        for m in DAY_WORD.finditer(text):
            w = re.sub(r"\s+", "", m["w"])
            if w in DEICTIC_DAY:
                day = a + timedelta(days=DEICTIC_DAY[w])
                out.append(self._rel(m, deictic, *_day_iv(day), G.DAY, day))
            else:
                anc = anaphoric or deictic
                day = anc.day + timedelta(days=ANAPHORIC_DAY[w])
                out.append(self._rel(m, anc, *_day_iv(day), G.DAY, day, fallback=anaphoric is None))

        for m in VAGUE_DAYS.finditer(text):
            if m["w"].startswith("엊"):
                s, e = _day_iv(a - timedelta(days=3))[0], _day_iv(a - timedelta(days=1))[1]
            else:
                s, e = _day_iv(a - timedelta(days=9))[0], _day_iv(a - timedelta(days=2))[1]
            out.append(self._rel(m, deictic, s, e, G.RANGE, vague=True))

        for pattern in (N_UNIT, NATIVE):
            for m in pattern.finditer(text):
                if pattern is N_UNIT:
                    n = int(m["n"]) if m["n"].isdigit() else NUM_WORDS[m["n"]]
                    unit = m["unit"]
                else:
                    n, unit = NATIVE_DAYS[m["w"]], "일"
                backward = m["dir"] in ("전", "前")
                anc = deictic if backward else (anaphoric or deictic)
                fallback = not backward and anaphoric is None
                sign = -1 if backward else 1
                if unit == "일":
                    day = anc.day + timedelta(days=sign * n)
                    out.append(self._rel(m, anc, *_day_iv(day), G.DAY, day, fallback))
                elif unit in ("주", "주일"):
                    center = anc.day + timedelta(days=sign * 7 * n)
                    s, e = _day_iv(center - timedelta(days=3))[0], _day_iv(center + timedelta(days=3))[1]
                    out.append(self._rel(m, anc, s, e, G.WEEK, fallback=fallback, vague=True))
                elif unit in ("개월", "달"):
                    y, mo = _add_months(anc.day, sign * n)
                    out.append(self._rel(m, anc, *_month_iv(y, mo), G.MONTH, fallback=fallback))
                else:
                    out.append(self._rel(m, anc, *_year_iv(anc.day.year + sign * n), G.YEAR, fallback=fallback))

        for m in WEEK_REL.finditer(text):
            offset = {"지지난": -2, "지난": -1, "저번": -1, "이번": 0, "다음": 1, "다다음": 2}[m["rel"]]
            monday = _monday(a) + timedelta(weeks=offset)
            if m["unit"] == "주말":
                s, e = _day_iv(monday + timedelta(days=5))[0], _day_iv(monday + timedelta(days=6))[1]
                out.append(self._rel(m, deictic, s, e, G.RANGE))
            elif m["wd"]:
                day = monday + timedelta(days=WEEKDAYS[m["wd"]])
                out.append(self._rel(m, deictic, *_day_iv(day), G.DAY, day))
            else:
                s = datetime.combine(monday, time())
                out.append(self._rel(m, deictic, s, s + timedelta(days=7), G.WEEK))

        for m in WEEKDAY_ALONE.finditer(text):
            target = WEEKDAYS[m["wd"]]
            rel = m["rel"]
            if rel == "다음":
                day = a + timedelta(days=(target - a.weekday()) % 7 or 7)
            elif rel == "이번":
                day = _monday(a) + timedelta(days=target)
            else:  # 수식어 없음/지난 → 기준일 이전 가장 가까운 그 요일
                back = (a.weekday() - target) % 7 or (7 if rel == "지난" else 0)
                day = a - timedelta(days=back)
            tm = self._rel(m, deictic, *_day_iv(day), G.DAY, day)
            tm.confidence *= 0.8
            out.append(tm)

        for m in MONTH_REL.finditer(text):
            offset = {"지지난": -2, "지난": -1, "저번": -1, "이번": 0, "다음": 1, "다다음": 2}[m["rel"]]
            y, mo = _add_months(a, offset)
            out.append(self._rel(m, deictic, *_month_iv(y, mo), G.MONTH))

        for m in MONTH_REL_NAMED.finditer(text):
            mo = int(m["m"])
            if not 1 <= mo <= 12:
                continue
            rel = m["rel"]
            if rel == "지난":
                y = a.year if mo < a.month else a.year - 1
            else:
                y = a.year + {"작년": -1, "올해": 0, "내년": 1}[rel]
            out.append(self._rel(m, deictic, *_month_iv(y, mo), G.MONTH))

        for m in YEAR_REL.finditer(text):
            w = re.sub(r"\s+", "", m["w"])
            if w == "이듬해":
                anc = anaphoric or deictic
                out.append(self._rel(m, anc, *_year_iv(anc.day.year + 1), G.YEAR, fallback=anaphoric is None))
                continue
            offset = {"재작년": -2, "작년": -1, "지난해": -1, "올해": 0, "금년": 0, "내년": 1, "다음해": 1}[w]
            out.append(self._rel(m, deictic, *_year_iv(a.year + offset), G.YEAR))
        return out

    # ── 시각 ──

    def _clocks(self, text: str) -> list[TimeMatch]:
        out = []
        for pattern in (CLOCK, KO_TIME):
            for m in pattern.finditer(text):
                h = int(m["h"])
                groups = m.groupdict()
                mi = int(groups["mi"]) if groups.get("mi") else (30 if groups.get("half") else 0)
                has_minute = bool(groups.get("mi") or groups.get("half"))
                if h > 24 or mi > 59:
                    continue
                ampm = groups.get("ampm")
                if ampm in ("오후", "저녁", "밤", "PM", "pm") and h < 12 or ampm == "낮" and h <= 6:
                    h += 12
                elif ampm in ("오전", "새벽", "아침", "AM", "am") and h == 12:
                    h = 0
                h %= 24
                ambiguous = ampm is None and 1 <= h <= 11 and not m["h"].startswith("0")
                base = datetime(2000, 1, 1, h, mi)
                step = timedelta(minutes=1) if has_minute else timedelta(hours=1)
                start, end = base, base + step
                approx = bool(groups.get("approx"))
                if approx:
                    start, end = start - timedelta(hours=1), end + timedelta(hours=1)
                cands = (
                    [TimeCandidate(start=start + timedelta(hours=12), end=end + timedelta(hours=12),
                                   reason="오전/오후 표기 없음")]
                    if ambiguous else []
                )
                value = TimeValue(
                    raw=m.group(0).strip(), start=start, end=end,
                    granularity=G.MINUTE if has_minute else G.HOUR, approximate=approx, candidates=cands,
                )
                lead = len(m.group(0)) - len(m.group(0).lstrip())
                out.append(TimeMatch(m.start() + lead, m.end(), value, 0.9, is_clock=True))
        return out

    def _dayparts(self, text: str) -> list[TimeMatch]:
        out = []
        for m in DAYPART.finditer(text):
            h0, h1 = DAYPART_HOURS[m["part"]]
            start = datetime(2000, 1, 1, h0)
            value = TimeValue(
                raw=m["part"], start=start, end=start + timedelta(hours=h1 - h0),
                granularity=G.HOUR, approximate=True, note="daypart",
            )
            out.append(TimeMatch(m.start(), m.end(), value, 0.8, is_clock=True))
        return out
