"""공소시효 계산 — 죄명에서 만료일까지.

기간표(statute_limitations.json)는 법정형 구간으로 되어 있고 사용자는 죄명으로 말한다.
그 사이를 offences.json 이 잇는다. 둘 중 하나라도 비면 계산하지 않는다.

장기·미제 사건에서 제일 위험한 실수는 **신법 기간으로 옛날 사건을 계산하는 것**이다.
2007-12-21 개정으로 기간이 늘었고 부칙에 따라 그 전 범행은 구법을 쓴다. 신법으로 계산하면
이미 끝난 사건을 '아직 남았다'고 안내하게 된다.
"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"

# 2007-12-21 법률 제8730호. 이 날 이전 범행은 구법.
AMENDMENT_DATE = date(2007, 12, 21)


@lru_cache(maxsize=1)
def load_limitations() -> dict[str, Any]:
    return json.loads((DATA / "statute_limitations.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_offences() -> dict[str, Any]:
    return json.loads((DATA / "offences.json").read_text(encoding="utf-8"))


def find_offence(name: str | None) -> dict[str, Any] | None:
    """죄명으로 법정형을 찾는다. 표에 없으면 None — 비슷한 죄명으로 대신 계산하지 않는다."""
    if not name:
        return None
    name = name.strip()
    for row in load_offences()["offences"]:
        if name == row["name"] or name in row.get("aliases", []):
            return row
    return None


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
        return {
            "resolved": True, "abolished": True, "offence": offence["name"],
            "statute": offence["statute"], "basis": offence.get("abolition_basis"),
            "note": "공소시효가 폐지된 범죄입니다. 다만 폐지 시행일 당시 이미 시효가 "
                    "완성된 사건에는 적용되지 않으므로 확인이 필요합니다.",
        }

    if incident_end is None:
        return {"resolved": False, "reason": "범행 종료일을 자료에서 찾지 못했습니다"}

    version = "old" if incident_end <= AMENDMENT_DATE else "current"
    table = next(v for v in load_limitations()["versions"] if v["id"] == version)
    row = next((b for b in table["brackets"] if b["max_penalty"] == offence["bracket"]), None)
    if row is None:
        return {"resolved": False,
                "reason": f"{version} 기간표에 '{offence['bracket']}' 구간이 없습니다 (구법 표가 아직 다 채워지지 않았습니다)"}

    years = row["years"]
    try:
        due = incident_end.replace(year=incident_end.year + years)
    except ValueError:  # 2월 29일
        due = incident_end.replace(year=incident_end.year + years, day=28)

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
