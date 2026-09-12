"""공공데이터 경찰관서 CSV → data/agencies.json.

    uv run python tools/import_agencies.py <csv...> --province 대구광역시경찰청

공공데이터포털(data.go.kr)의 '관서별 지역경찰 현황' 계열 파일을 받는다. 파일에 따라
컬럼 이름이 조금씩 다르고 인코딩은 대개 cp949 다.

이 자료에는 **지구대·파출소의 주소만 있고 경찰서 자체의 주소는 없다.** 제출처는 경찰서장
또는 상급경찰관서장이므로 주소는 따로 채워야 한다 — 그 사실을 address: null 로 남긴다.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from pathlib import Path

OUT = Path(__file__).parent.parent / "src" / "action_engine" / "data" / "agencies.json"
ENCODINGS = ("cp949", "euc-kr", "utf-8-sig")


def read_rows(path: Path) -> list[dict[str, str]]:
    for enc in ENCODINGS:
        try:
            with path.open(encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except (UnicodeDecodeError, LookupError):
            continue
    raise SystemExit(f"인코딩을 알 수 없습니다: {path}")


def column(row: dict[str, str], *names: str) -> str:
    for n in names:
        if n in row and row[n]:
            return row[n].strip()
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+", type=Path)
    ap.add_argument("--province", required=True, help="상급경찰관서 이름 (예: 대구광역시경찰청)")
    args = ap.parse_args()

    stations: OrderedDict[str, dict] = OrderedDict()
    for path in args.csv:
        rows = read_rows(path)
        if not rows:
            print(f"  건너뜀 (빈 파일): {path.name}")
            continue
        # 같은 '경찰서' 컬럼을 쓰면서도 주소 없이 연도별 개수만 담은 통계표가 섞여 있다.
        # 그런 파일을 그대로 넣으면 다른 시·도 경찰서가 엉뚱한 상급관서 밑에 붙는다.
        if not column(rows[0], "경찰서") or "주소" not in rows[0]:
            print(f"  건너뜀 (관서 목록이 아니라 통계표로 보임): {path.name}")
            continue

        for r in rows:
            name = column(r, "경찰서")
            if not name:
                continue
            st = stations.setdefault(name, {
                "type": "police_station",
                "name": name if name.endswith("경찰서") else f"{name}경찰서",
                "parent": args.province,
                "address": None,
                "phone": None,
                "local_offices": [],
            })
            office = column(r, "지구대(파출소)명", "지역경찰관서명", "관서명")
            if office:
                st["local_offices"].append({
                    "name": office,
                    "kind": column(r, "구분"),
                    "phone": column(r, "전화번호"),
                    "address": column(r, "주소"),
                })
        print(f"  읽음: {path.name} ({len(rows)}행)")

    data = {
        "status": "partial" if stations else "empty",
        "note": "공공데이터 경찰관서 자료에서 만들었다. 경찰서의 상하 관계와 지역경찰관서 주소는 있지만 "
                "경찰서 자체의 주소·전화는 원자료에 없어 비어 있다. 제출처는 경찰서장 또는 상급경찰관서장이므로 "
                "그 주소를 따로 채워야 화면이 구체적인 안내를 할 수 있다.",
        "generated_by": "tools/import_agencies.py",
        "covered_regions": [args.province],
        "known_gaps": [
            "경찰서 자체의 주소·전화 (원자료에 없음)",
            f"{args.province} 외 지역 (같은 명령으로 다른 시·도 파일을 추가하면 된다)",
            "검찰청·법원 관할 (별도 자료 필요)",
        ],
        "agencies": [
            {"type": "provincial_police", "name": args.province, "parent": "경찰청",
             "address": None, "phone": None},
            *stations.values(),
        ],
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    offices = sum(len(s["local_offices"]) for s in stations.values())
    print(f"\n{OUT.name} 생성 — 경찰서 {len(stations)}개 · 지역관서 {offices}개")


if __name__ == "__main__":
    main()
