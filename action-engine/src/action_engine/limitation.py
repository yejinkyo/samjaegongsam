"""공소시효 계산 — 죄명에서 만료일까지.

기간표(statute_limitations.json)는 법정형 구간으로 되어 있고 사용자는 죄명으로 말한다.
그 사이를 offences.json 이 잇는다. 둘 중 하나라도 비면 계산하지 않는다.

장기·미제 사건에서 제일 위험한 실수는 **신법 기간으로 옛날 사건을 계산하는 것**이다.
2007-12-21 개정으로 기간이 늘었고 부칙에 따라 그 전 범행은 구법을 쓴다. 신법으로 계산하면
이미 끝난 사건을 '아직 남았다'고 안내하게 된다.
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"

# 2007-12-21 법률 제8730호. 이 날 이전 범행은 구법.
AMENDMENT_DATE = date(2007, 12, 21)
# 2015-07-31 법률 제13454호(제253조의2 살인죄 공소시효 배제). 부칙 제2조 — 시행 당시 아직 시효가
# 완성되지 않은 범죄에만 적용된다. 그 전에 이미 끝난 사건은 되살아나지 않는다.
ABOLITION_DATE = date(2015, 7, 31)


@lru_cache(maxsize=1)
def load_limitations() -> dict[str, Any]:
    return json.loads((DATA / "statute_limitations.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_offences() -> dict[str, Any]:
    return json.loads((DATA / "offences.json").read_text(encoding="utf-8"))


def _key(name: str) -> str:
    """표기만 다른 죄명을 같게 본다 — 통지서마다 '미성년자 약취·유인' · '미성년자약취유인' 처럼 적는다."""
    return re.sub(r"[\s·ㆍ.,]", "", name).removesuffix("죄")


def find_offence(name: str | None) -> dict[str, Any] | None:
    """죄명으로 법정형을 찾는다. 표에 없으면 None — 비슷한 죄명으로 대신 계산하지 않는다.

    띄어쓰기 · 가운뎃점 · 끝의 '죄' 만 무시한다. '약취유인' 을 '미성년자 약취·유인' 으로 읽는 식의
    짐작은 하지 않는다 — 대상이 미성년자인지, 무슨 목적인지에 따라 법정형이 다르다.
    """
    if not name:
        return None
    key = _key(name)
    for row in load_offences()["offences"]:
        if key in {_key(n) for n in [row["name"], *row.get("aliases", [])]}:
            return row
    return None


def expiry_date(incident_end: date, years: int) -> date:
    """공소시효가 완성되는 날(이 날이 지나면 공소를 제기할 수 없다).

    시효는 초일을 산입한다(형사소송법 제66조 제1항 단서) — 범행 종료일이 첫날이다. 그래서 N년 뒤
    같은 날의 **전날**에 끝난다(민법 제160조 제2항). 그 달에 같은 날이 없으면(2월 29일) 그 달 말일에
    끝난다(같은 조 제3항). 말일이 공휴일이어도 늘어나지 않는다(형사소송법 제66조 제3항 단서).
    """
    try:
        return incident_end.replace(year=incident_end.year + years) - timedelta(days=1)
    except ValueError:  # 2월 29일
        return date(incident_end.year + years, 2, 28)


def _period(offence: dict[str, Any], incident_end: date) -> tuple[str, int | None]:
    """범행일에 적용되는 기간표와 연수. 표에 그 구간이 없으면 연수는 None."""
    version = "old" if incident_end <= AMENDMENT_DATE else "current"
    table = next(v for v in load_limitations()["versions"] if v["id"] == version)
    row = next((b for b in table["brackets"] if b["max_penalty"] == offence["bracket"]), None)
    return version, row["years"] if row else None


def _abolished(offence: dict[str, Any], incident_end: date | None, as_of: date) -> dict[str, Any]:
    """시효가 폐지된 범죄. 폐지 시행일에 종전 시효가 아직 남아 있었는지까지 따진다."""
    base = {"resolved": True, "offence": offence["name"], "statute": offence["statute"],
            "basis": offence.get("abolition_basis")}
    if incident_end is None:
        return {**base, "abolished": True,
                "note": "공소시효가 폐지된 범죄입니다. 다만 2015-07-31 폐지 시행 당시 이미 시효가 완성된 사건에는 "
                        "적용되지 않습니다(형사소송법 부칙 <제13454호> 제2조). 범행일을 알아야 확인할 수 있습니다."}
    version, years = _period(offence, incident_end)
    if years is None:
        return {**base, "abolished": True,
                "note": f"공소시효가 폐지된 범죄입니다. {version} 기간표가 비어 있어 폐지 시행 당시 시효가 남아 있었는지는 확인하지 못했습니다."}
    old_due = expiry_date(incident_end, years)
    if old_due < ABOLITION_DATE:
        # 폐지되기 전에 이미 끝났다 — 폐지 규정이 적용되지 않는다
        return {**base, "abolished": False, "penalty": offence["penalty"], "bracket": offence["bracket"],
                "version": version, "years": years, "incident_end": incident_end, "due_date": old_due,
                "days_left": (old_due - as_of).days,
                "version_note": (f"2015-07-31 공소시효 폐지 전에 종전 시효({years}년)가 {old_due:%Y-%m-%d}에 이미 "
                                 "완성되어 폐지 규정이 적용되지 않습니다(형사소송법 부칙 <제13454호> 제2조)"),
                "caveat": "시효 정지 기간(공소 제기, 범인의 국외 도피 등)은 빼지 않은 값입니다."}
    return {**base, "abolished": True,
            "note": (f"공소시효가 폐지된 범죄입니다. 범행일({incident_end:%Y-%m-%d}) 기준 종전 시효({years}년)가 "
                     f"{old_due:%Y-%m-%d}까지 남아 있어 2015-07-31 폐지가 적용됩니다(형사소송법 제253조의2, "
                     "부칙 <제13454호> 제2조).")}


def compute_limitation(offence_name: str | None, incident_end: date | None, as_of: date) -> dict[str, Any]:
    """공소시효 만료일을 계산한다.

    돌려주는 dict 는 항상 ``resolved`` 를 가진다. False 면 ``reason`` 에 왜 못 했는지가 있고,
    화면은 D-day 를 그리지 않는다.
    """
    offence = find_offence(offence_name)
    if offence is None:
        return {"resolved": False,
                "reason": f"'{offence_name}' 의 법정형을 표에서 찾지 못했습니다" if offence_name
                          else "죄명 정보가 없어 계산할 수 없습니다"}

    if offence.get("limitation_abolished"):
        return _abolished(offence, incident_end, as_of)

    if incident_end is None:
        return {"resolved": False, "reason": "범행 종료일을 자료에서 찾지 못했습니다"}

    version, years = _period(offence, incident_end)
    if years is None:
        return {"resolved": False,
                "reason": f"{version} 기간표에 '{offence['bracket']}' 구간이 없습니다 (구법 표가 아직 다 채워지지 않았습니다)"}
    due = expiry_date(incident_end, years)

    return {
        "resolved": True, "abolished": False,
        "offence": offence["name"], "statute": offence["statute"],
        "penalty": offence["penalty"], "bracket": offence["bracket"],
        "version": version, "years": years,
        "incident_end": incident_end, "due_date": due,
        "days_left": (due - as_of).days,
        "version_note": ("2007-12-21 개정 전 범행이라 구법 기간을 적용했습니다"
                         if version == "old" else "2007-12-21 개정 후 범행입니다"),
        "caveat": "시효 정지 기간(공소 제기, 범인의 국외 도피 등)은 빼지 않은 값입니다.",
    }
