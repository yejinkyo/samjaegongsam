"""배포용 정리 API — 올린 자료를 두 엔진에 넣고 사건 화면 데이터를 돌려준다.

    POST /api/analyze   (Vercel 함수)

로컬 정리 서버(web/serve.py)와 달리 **아무것도 저장하지 않는다.** 화면이 사건 하나의 자료 전체
(OCR 결과 · 직접 적은 메모)를 보내면 그대로 엔진을 돌려 결과만 돌려준다. 사진은 브라우저가 읽고
(tesseract.js) 읽은 글자만 보낸다. 사건과 원본 사진은 그 브라우저에만 남는다(web/assets/browser-store.js).

    요청  {case_id, case_type, title, as_of, documents: [OcrDocument…], user_notes: [UserNote…]}
    응답  사건 화면 데이터 — action-engine/tools/export_web.py 의 build_view 와 같은 모양

두 엔진은 설치하지 않고 저장소 안의 소스를 그대로 불러온다. 함수가 설치하는 것은 두 엔진의
런타임 의존성뿐이다(저장소 루트 requirements.txt).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _src in (ROOT / "research-engine" / "src", ROOT / "action-engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from pydantic import ValidationError  # noqa: E402

from research_engine.pipeline import CaseInput, ResearchPipeline  # noqa: E402
from research_engine.requirements import available_case_types, load_requirements  # noqa: E402

CASE_ID = re.compile(r"^[0-9a-f]{12}$")
MAX_BODY_BYTES = 4 * 1024 * 1024   # Vercel 함수 본문 한도(4.5MB) 안쪽
MAX_DOCUMENTS = 60
MAX_TITLE = 60


class ApiError(Exception):
    def __init__(self, status: HTTPStatus, message: str, detail: str | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.detail = detail


def case_types() -> list[dict]:
    """엔진이 실제로 다루는 사건 유형. 화면의 유형 목록은 여기서만 온다."""
    out = []
    for case_type in available_case_types():
        req = load_requirements(case_type)
        out.append({"type": req.case_type, "label": req.label, "status": req.status})
    return out


_build_view = None


def build_view(case_id: str, title: str, result: dict) -> dict:
    """화면 데이터 변환은 스크립트(tools/export_web.py) 안에 있다. 예시 사건과 같은 모양을 내려고 그대로 쓴다."""
    global _build_view
    if _build_view is None:
        spec = importlib.util.spec_from_file_location("export_web", ROOT / "action-engine" / "tools" / "export_web.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        _build_view = module.build_view
    # 내보내기 스크립트는 명령줄용 안내('문장 다듬기를 건너뜁니다')를 stdout 에 찍는다. 응답과 섞이지 않게 버린다.
    with contextlib.redirect_stdout(io.StringIO()):
        return _build_view(case_id, title, result)


def analyze(payload: dict) -> dict:
    types = {t["type"]: t for t in case_types()}
    case_type = str(payload.get("case_type") or "")
    if case_type not in types:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "사건 유형을 골라 주세요.")
    case_id = str(payload.get("case_id") or "")
    if not CASE_ID.match(case_id):
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "사건 번호 형식이 맞지 않아요.")
    try:
        as_of = date.fromisoformat(str(payload.get("as_of") or ""))
    except ValueError:
        as_of = date.today()

    documents = payload.get("documents") or []
    notes = [n for n in payload.get("user_notes") or [] if isinstance(n, dict) and str(n.get("text") or "").strip()]
    if not isinstance(documents, list) or len(documents) > MAX_DOCUMENTS:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, f"자료는 한 사건에 {MAX_DOCUMENTS}개까지 정리할 수 있어요.")
    if not documents and not notes:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "올린 자료가 없어요. 사진이나 메모를 하나 이상 더해 주세요.")

    title = str(payload.get("title") or "").strip()[:MAX_TITLE] or f"{types[case_type]['label']} ({as_of:%Y.%m.%d} 등록)"
    try:
        case = CaseInput.model_validate({
            "case_id": case_id,
            "case_type": case_type,
            "as_of": as_of,
            "documents": documents,
            "user_notes": notes,
        })
    except ValidationError as err:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "자료 형식을 읽지 못했어요.", str(err).splitlines()[0]) from None

    result = ResearchPipeline().run(case)
    return build_view(case_id, title, json.loads(result.model_dump_json()))


class handler(BaseHTTPRequestHandler):
    def send_json(self, status: HTTPStatus, data) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                raise ApiError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "한 번에 보낼 수 있는 크기를 넘었어요. 자료를 나눠서 더해 주세요.")
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ApiError(HTTPStatus.BAD_REQUEST, "요청을 읽지 못했어요.") from None
            if not isinstance(payload, dict):
                raise ApiError(HTTPStatus.BAD_REQUEST, "요청을 읽지 못했어요.")
            self.send_json(HTTPStatus.OK, analyze(payload))
        except ApiError as err:
            self.send_json(err.status, {"error": err.message, "detail": err.detail})
        except Exception as err:  # noqa: BLE001 — 연결을 끊지 말고 화면이 이유를 보여 줄 수 있게 한다
            sys.stderr.write(f"POST /api/analyze: {err!r}\n")
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "자료를 정리하다가 엔진이 멈췄어요.", "detail": repr(err)})

    def do_GET(self) -> None:
        self.send_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "POST 로 보내 주세요."})
