"""배포용 상태 API — 화면이 '어떤 방식으로 정리하는가'를 묻는다.

    GET /api/status   (Vercel 함수)

로컬 정리 서버(web/serve.py)는 사건을 서버에 저장하고 사진도 서버가 읽는다. 배포 환경은
저장하지 않으므로 mode 를 "browser" 로 알린다 — 화면은 사진을 브라우저에서 읽고, 사건을
브라우저에 저장하고, 정리만 /api/analyze 에 맡긴다.
"""

from __future__ import annotations

import sys
from http import HTTPStatus
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze import case_types  # noqa: E402
from analyze import handler as _json_handler


def status() -> dict:
    return {
        "mode": "browser",
        "ocr": {"ready": True, "reason": None, "where": "browser"},
        "case_types": case_types(),
    }


class handler(_json_handler):
    def do_GET(self) -> None:
        self.send_json(HTTPStatus.OK, status())

    def do_POST(self) -> None:
        self.send_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "GET 으로 요청해 주세요."})
