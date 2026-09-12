"""기관 조회 — 제출처를 구체적인 관서 이름으로 바꾼다.

``submit_to`` 문구는 "바로 위 상급경찰관서의 장"처럼 관계로만 적혀 있다. 사용자는 그 말로는
어디로 가야 할지 모른다. 이 모듈이 실제 관서 이름을 붙인다.

자료가 없는 지역은 문구를 그대로 둔다 — 없는 기관을 지어내지 않는다.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def load_agencies() -> dict[str, Any]:
    return json.loads((DATA / "agencies.json").read_text(encoding="utf-8"))


def find_agency(name: str | None) -> dict[str, Any] | None:
    """관서 이름으로 찾는다. '대구중부', '대구중부경찰서' 둘 다 받는다."""
    if not name:
        return None
    name = name.strip()
    for a in load_agencies().get("agencies", []):
        if name == a["name"] or f"{name}경찰서" == a["name"]:
            return a
    return None


def find_parent(name: str | None) -> dict[str, Any] | None:
    """바로 위 상급관서. 수사중지 이의제기서를 내는 곳이다 (경찰수사규칙 제101조)."""
    agency = find_agency(name)
    if agency is None or not agency.get("parent"):
        return None
    return find_agency(agency["parent"]) or {"name": agency["parent"], "address": None, "phone": None}


def describe_submit_to(template: str | None, station: str | None) -> dict[str, Any]:
    """제출처 문구에 실제 관서를 붙인다.

    ``resolved`` 가 False 면 자료에 없다는 뜻이고, 화면은 원래 문구만 보여준다.
    """
    out: dict[str, Any] = {"text": template, "resolved": False}
    if not station:
        out["reason"] = "사건을 담당한 경찰관서를 알 수 없습니다"
        return out

    agency = find_agency(station)
    if agency is None:
        out["reason"] = f"'{station}' 이(가) 기관 자료에 없습니다 (수집된 지역: " \
                        f"{', '.join(load_agencies().get('covered_regions', [])) or '없음'})"
        return out

    out["station"] = {"name": agency["name"], "address": agency.get("address"), "phone": agency.get("phone")}
    if template and "상급경찰관서" in template:
        parent = find_parent(station)
        if parent is None:
            out["reason"] = "상급관서를 찾지 못했습니다"
            return out
        out["target"] = parent
        out["resolved"] = True
        out["hint"] = f"{agency['name']}에 제출하면 {parent['name']}으로 송부됩니다"
    else:
        out["target"] = out["station"]
        out["resolved"] = True
    return out
