"""화면 서버 — 정적 파일과 사건 등록 API.

    py web/serve.py          # 기본 8765
    py web/serve.py 9000

정적 파일: `python -m http.server` 는 캐시 헤더를 주지 않아서, 브라우저가 고친 HTML·CSS 를
안 받아 오고 옛 화면을 계속 보여 준다. 여기서는 매번 새로 받게 한다.

사건 등록: 화면에서 올린 자료를 엔진에 실제로 넣는다.

    올린 사진·OCR JSON·메모 → local-cases/<id>/case.json
      → research-engine run (사진은 Tesseract 로 읽는다) → result.json
      → action-engine tools/export_web.py --result → view.json → 화면

두 엔진은 서로 import 하지 않는 별도 패키지라 각 폴더에서 `uv run` 으로 부른다.
이 서버는 표준 라이브러리만 쓴다. 등록한 사건과 올린 파일은 local-cases/ 에만 남는다
(gitignore — 커밋되지 않고, 어디로도 보내지 않는다).

GitHub Pages 에는 이 서버가 없다. 화면은 API 가 없으면 등록을 막고 그 이유를 보여준다.

OCR 설정 (환경 변수, 없으면 기본 위치를 찾는다)
    TESSERACT_CMD     tesseract 실행 파일. 기본: PATH → C:/Program Files/Tesseract-OCR/tesseract.exe
    TESSDATA_PREFIX   kor.traineddata 가 있는 폴더. 기본: ~/.tarae/tessdata (있으면)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import date, datetime
from email.parser import BytesParser
from email.policy import HTTP
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
RESEARCH = REPO / "research-engine"
ACTION = REPO / "action-engine"
REQUIREMENTS = RESEARCH / "src" / "research_engine" / "requirements"
CASES_DIR = Path(os.environ.get("TARAE_CASES_DIR", REPO / "local-cases"))

MAX_UPLOAD_BYTES = 40 * 1024 * 1024
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
CASE_ID = re.compile(r"^[0-9a-f]{12}$")
RUN_TIMEOUT = 600

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


class ApiError(Exception):
    def __init__(self, status: HTTPStatus, message: str, detail: str | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.detail = detail


# ── 설정 ────────────────────────────────────────────────────────────────


def tesseract_cmd() -> str | None:
    for candidate in (os.environ.get("TESSERACT_CMD"), shutil.which("tesseract"), r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def tessdata_dir() -> str | None:
    if os.environ.get("TESSDATA_PREFIX"):
        return os.environ["TESSDATA_PREFIX"]
    # AppData 아래는 스토어판 파이썬이 다른 폴더로 보여 줘서 찾지 못한다 — 홈 폴더에 둔다
    local = Path.home() / ".tarae" / "tessdata"
    return str(local) if (local / "kor.traineddata").is_file() else None


def ocr_status() -> dict:
    cmd = tesseract_cmd()
    if not cmd:
        return {"ready": False, "reason": "Tesseract 가 설치되어 있지 않아 사진을 읽을 수 없어요."}
    data = tessdata_dir()
    kor = Path(data, "kor.traineddata") if data else Path(cmd).parent / "tessdata" / "kor.traineddata"
    if not kor.is_file():
        return {"ready": False, "reason": "Tesseract 한국어 데이터(kor.traineddata)가 없어 사진을 읽을 수 없어요."}
    return {"ready": True, "reason": None}


def case_types() -> list[dict]:
    """엔진이 실제로 다루는 사건 유형. 화면의 유형 목록은 여기서만 온다."""
    out = []
    for path in sorted(REQUIREMENTS.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        out.append({"type": raw["case_type"], "label": raw["label"], "status": raw.get("status")})
    return out


# ── 사건 저장소 ──────────────────────────────────────────────────────────


def case_lock(case_id: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(case_id, threading.Lock())


def case_dir(case_id: str) -> Path:
    if not CASE_ID.match(case_id):
        raise ApiError(HTTPStatus.NOT_FOUND, "사건을 찾지 못했어요.")
    path = CASES_DIR / case_id
    if not (path / "meta.json").is_file():
        raise ApiError(HTTPStatus.NOT_FOUND, "사건을 찾지 못했어요.")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# 원본을 내줄 때 브라우저에 알려 줄 형식. 목록에 없는 확장자는 내주지 않는다 —
# 사건 폴더에 무엇이 들어오든 아무 파일이나 열어 주는 통로가 되면 안 된다.
VIEWABLE_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
    ".json": "application/json",
}


def upload_path(folder: Path, doc_id: str) -> tuple[Path, str]:
    """사건 안의 doc_id 로 올린 원본을 찾는다. 경로를 밖에서 받지 않는 것이 핵심이다 —
    파일 이름을 그대로 받으면 사건 폴더 밖을 가리킬 수 있다."""
    meta = read_json(folder / "meta.json")
    doc = next((d for d in meta.get("documents", []) if d.get("doc_id") == doc_id), None)
    if not doc:
        raise ApiError(HTTPStatus.NOT_FOUND, "그 자료를 찾지 못했어요.")

    stored = Path(doc["stored"]).name          # 폴더 구분자가 섞여 와도 이름만 쓴다
    media = VIEWABLE_TYPES.get(Path(stored).suffix.lower())
    if not media:
        raise ApiError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "이 형식은 화면에서 열 수 없어요.")

    path = (folder / "uploads" / stored).resolve()
    if not path.is_file() or folder.resolve() not in path.parents:
        raise ApiError(HTTPStatus.NOT_FOUND, "그 자료를 찾지 못했어요.")
    return path, media


def with_files(view: dict, folder: Path) -> dict:
    """화면이 원본을 열 수 있게 자료마다 주소를 붙인다.

    예시 사건(cases.js)에는 올린 파일이 없다. 그때는 주소를 붙이지 않고, 화면은
    누를 수 없는 상태로 그린다 — 눌러도 아무 일이 없는 것보다 낫다.
    """
    meta = read_json(folder / "meta.json")
    stored = {d["doc_id"]: d["stored"] for d in meta.get("documents", [])}
    def mark(src: dict) -> None:
        doc_id = src.get("doc_id")
        media = VIEWABLE_TYPES.get(Path(stored.get(doc_id, "")).suffix.lower()) if doc_id in stored else None
        if not media:
            return
        src["href"] = f"api/cases/{view['id']}/files/{doc_id}"
        # 화면이 보는 이름은 자료 이름(사진)인데 올린 파일은 OCR 결과 JSON 일 수 있다.
        # 무엇으로 열지는 저장된 형식이 정한다 — 이름으로 짐작하면 틀린다.
        src["media"] = media

    for src in view.get("sources") or []:
        mark(src)
    # 타임라인의 '자세히' 에서도 그 줄이 어느 원본에서 왔는지 바로 열 수 있어야 한다
    for row in view.get("timeline") or []:
        for src in row.get("sources") or []:
            mark(src)
    return view


def load_view(folder: Path) -> dict:
    """화면 데이터 + 이 서버에서 만든 사건이라는 표시(local). 화면은 local 일 때만 자료 추가를 연다."""
    view = read_json(folder / "view.json")
    view["created_at"] = read_json(folder / "meta.json").get("created_at")
    view["local"] = True
    return with_files(view, folder)


def list_views() -> list[dict]:
    if not CASES_DIR.is_dir():
        return []
    views = []
    for meta_path in CASES_DIR.glob("*/meta.json"):
        view_path = meta_path.parent / "view.json"
        if view_path.is_file():
            views.append(load_view(meta_path.parent))
    return sorted(views, key=lambda v: v.get("created_at") or "", reverse=True)


def add_uploads(folder: Path, meta: dict, form: dict) -> None:
    """올린 파일과 메모를 사건 폴더에 더한다. 읽을 수 없는 형식은 조용히 버리지 않고 거절한다."""
    uploads = folder / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    rejected = [f["filename"] for f in form["files"] if Path(f["filename"]).suffix.lower() not in IMAGE_EXTS | {".json"}]
    if rejected:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY,
                       "아직 읽을 수 없는 형식이 있어요: " + ", ".join(rejected) + " — 사진(이미지)이나 OCR 결과 JSON 만 정리할 수 있어요.")
    if any(Path(f["filename"]).suffix.lower() in IMAGE_EXTS for f in form["files"]):
        status = ocr_status()
        if not status["ready"]:
            raise ApiError(HTTPStatus.SERVICE_UNAVAILABLE, status["reason"])

    for n, f in enumerate(form["files"]):
        suffix = Path(f["filename"]).suffix.lower()
        doc_id = f"doc{len(meta['documents']) + 1}"
        stored = f"{doc_id}{suffix}"
        if suffix == ".json":
            try:
                doc = json.loads(f["data"].decode("utf-8"))
                assert isinstance(doc, dict) and isinstance(doc.get("pages"), list)
            except (ValueError, AssertionError):
                raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, f"{f['filename']} 은 OCR 결과 JSON 형식이 아니에요.") from None
            # 사건 안에서 문서 id 가 겹치지 않게 서버가 새로 붙인다. 파일 이름은 사용자가 올린 그대로 둔다.
            doc.update(doc_id=doc_id, file_name=doc.get("file_name") or f["filename"])
            write_json(uploads / stored, doc)
        else:
            (uploads / stored).write_bytes(f["data"])
        meta["documents"].append({
            "doc_id": doc_id,
            "file_name": f["filename"],
            "stored": stored,
            "captured_at": form["modified"][n] if n < len(form["modified"]) else None,
        })
    now = datetime.now().isoformat(timespec="seconds")
    for text in form["notes"]:
        if text.strip():
            meta["notes"].append({"note_id": f"note{len(meta['notes']) + 1}", "text": text.strip(), "created_at": now})
    if not meta["documents"] and not meta["notes"]:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "올린 자료가 없어요. 사진이나 메모를 하나 이상 더해 주세요.")


def build_case_input(folder: Path, meta: dict) -> dict:
    documents, images = [], []
    for d in meta["documents"]:
        if d["stored"].endswith(".json"):
            documents.append(f"uploads/{d['stored']}")
        else:
            images.append({
                "doc_id": d["doc_id"],
                "file_name": d["file_name"],
                "image_paths": [str(folder / "uploads" / d["stored"])],
                "captured_at": d.get("captured_at"),
            })
    return {
        "case_id": meta["id"],
        "case_type": meta["case_type"],
        "as_of": date.today().isoformat(),
        "documents": documents,
        "images": images,
        "user_notes": meta["notes"],
    }


def run(cmd: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=RUN_TIMEOUT)
    out = proc.stdout.decode("utf-8", "replace") + proc.stderr.decode("utf-8", "replace")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"$ {' '.join(cmd)}  (in {cwd.name})\n{out}\n")
    if proc.returncode != 0:
        tail = "\n".join(line for line in out.strip().splitlines()[-6:])
        raise ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, "자료를 정리하다가 엔진이 멈췄어요.", tail)


def analyze(folder: Path, meta: dict) -> dict:
    """사건 폴더 하나를 두 엔진에 통과시켜 view.json 을 만든다."""
    uv = shutil.which("uv")
    if not uv:
        raise ApiError(HTTPStatus.SERVICE_UNAVAILABLE, "uv 가 설치되어 있지 않아 엔진을 돌릴 수 없어요.")
    write_json(folder / "case.json", build_case_input(folder, meta))
    log = folder / "run.log"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    cmd = [uv, "run", "research-engine", "run", str(folder / "case.json"), "--out", str(folder / "result.json")]
    if any(not d["stored"].endswith(".json") for d in meta["documents"]):
        cmd = [uv, "run", "--extra", "ocr", *cmd[2:], "--ocr", "tesseract", "--tesseract-cmd", tesseract_cmd() or "tesseract"]
        if tessdata_dir():
            env["TESSDATA_PREFIX"] = tessdata_dir()  # type: ignore[assignment]
    run(cmd, RESEARCH, log, env)
    run([uv, "run", "python", "tools/export_web.py", "--result", str(folder / "result.json"),
         "--id", meta["id"], "--title", meta["title"], "--out", str(folder / "view.json")], ACTION, log, env)
    write_json(folder / "meta.json", meta)
    return load_view(folder)


def create_case(form: dict) -> dict:
    types = {t["type"]: t for t in case_types()}
    case_type = (form["fields"].get("case_type") or "").strip()
    if case_type not in types:
        raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, "사건 유형을 골라 주세요.")
    now = datetime.now()
    case_id = uuid.uuid4().hex[:12]
    title = (form["fields"].get("title") or "").strip()[:60] or f"{types[case_type]['label']} ({now:%Y.%m.%d} 등록)"
    meta = {"id": case_id, "title": title, "case_type": case_type, "created_at": now.isoformat(timespec="seconds"),
            "documents": [], "notes": []}
    folder = CASES_DIR / case_id
    folder.mkdir(parents=True)
    try:
        add_uploads(folder, meta, form)
        with case_lock(case_id):
            return analyze(folder, meta)
    except ApiError as err:
        if not (folder / "view.json").is_file():
            # 한 번도 정리되지 않은 사건은 목록에 남기지 않는다. 엔진이 멈춘 기록은 로그로 남긴다.
            if err.status == HTTPStatus.INTERNAL_SERVER_ERROR and (folder / "run.log").is_file():
                failed = CASES_DIR / "_failed"
                failed.mkdir(parents=True, exist_ok=True)
                shutil.copy(folder / "run.log", failed / f"{case_id}.log")
            shutil.rmtree(folder, ignore_errors=True)
        raise


def add_to_case(case_id: str, form: dict) -> dict:
    folder = case_dir(case_id)
    with case_lock(case_id):
        meta = read_json(folder / "meta.json")
        before = json.dumps(meta)
        add_uploads(folder, meta, form)
        try:
            view = analyze(folder, meta)
        except ApiError:
            # 새 자료로 정리에 실패하면 사건을 올리기 전 상태로 되돌린다
            restored = json.loads(before)
            for d in meta["documents"][len(restored["documents"]):]:
                (folder / "uploads" / d["stored"]).unlink(missing_ok=True)
            write_json(folder / "meta.json", restored)
            raise
        return view


# ── HTTP ────────────────────────────────────────────────────────────────


def parse_form(content_type: str, body: bytes) -> dict:
    """multipart/form-data → {fields, files, notes, modified}. 표준 라이브러리 email 파서를 쓴다."""
    if not content_type.startswith("multipart/form-data"):
        raise ApiError(HTTPStatus.BAD_REQUEST, "multipart/form-data 로 보내 주세요.")
    msg = BytesParser(policy=HTTP).parsebytes(b"Content-Type: " + content_type.encode("latin-1") + b"\r\n\r\n" + body)
    form: dict = {"fields": {}, "files": [], "notes": [], "modified": []}
    for part in msg.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        data = part.get_payload(decode=True) or b""
        if filename is not None:
            # 브라우저는 파일 이름을 UTF-8 그대로 보내는데 email 파서는 ASCII 로 읽는다
            filename = filename.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
            form["files"].append({"filename": Path(filename).name, "data": data})
        elif name == "note":
            form["notes"].append(data.decode("utf-8"))
        elif name == "modified":
            form["modified"].append(data.decode("utf-8") or None)
        elif name:
            form["fields"][name] = data.decode("utf-8")
    return form


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        """404·500 만 남긴다 — 링크가 끊겼는지는 봐야 하고, 200 로그는 시끄럽다."""
        line = fmt % args
        if " 404 " in line or " 500 " in line:
            sys.stderr.write(f"{line}\n")

    def send_json(self, status: HTTPStatus, data) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_api(self, method: str) -> None:
        path = self.path.split("?", 1)[0].rstrip("/")
        try:
            if method == "GET" and path == "/api/status":
                return self.send_json(HTTPStatus.OK, {"ocr": ocr_status(), "case_types": case_types()})
            if method == "GET" and path == "/api/cases":
                return self.send_json(HTTPStatus.OK, list_views())
            m = re.fullmatch(r"/api/cases/([^/]+)", path)
            if method == "GET" and m:
                folder = case_dir(m[1])
                if not (folder / "view.json").is_file():
                    raise ApiError(HTTPStatus.NOT_FOUND, "사건을 찾지 못했어요.")
                return self.send_json(HTTPStatus.OK, load_view(folder))
            f = re.fullmatch(r"/api/cases/([^/]+)/files/([^/]+)", path)
            if method == "GET" and f:
                return self.send_file(*upload_path(case_dir(f[1]), f[2]))
            if method == "POST" and (path == "/api/cases" or re.fullmatch(r"/api/cases/[^/]+/files", path)):
                length = int(self.headers.get("Content-Length") or 0)
                if length > MAX_UPLOAD_BYTES:
                    raise ApiError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "한 번에 올릴 수 있는 크기(40MB)를 넘었어요.")
                form = parse_form(self.headers.get("Content-Type", ""), self.rfile.read(length))
                if path == "/api/cases":
                    return self.send_json(HTTPStatus.CREATED, create_case(form))
                return self.send_json(HTTPStatus.OK, add_to_case(path.split("/")[3], form))
            raise ApiError(HTTPStatus.NOT_FOUND, "없는 주소예요.")
        except ApiError as err:
            self.send_json(err.status, {"error": err.message, "detail": err.detail})
        except subprocess.TimeoutExpired:
            self.send_json(HTTPStatus.GATEWAY_TIMEOUT, {"error": "정리가 너무 오래 걸려 멈췄어요. 사진 수를 줄여 다시 올려 주세요."})
        except UnicodeDecodeError:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "글자를 UTF-8 로 읽지 못했어요."})
        except Exception as err:  # noqa: BLE001 — 연결을 끊지 말고 화면이 이유를 보여 줄 수 있게 한다
            sys.stderr.write(f"{self.command} {self.path}: {err!r}\n")
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "서버에서 처리하지 못했어요.", "detail": repr(err)})

    def send_file(self, path: Path, media: str) -> None:
        """올린 원본을 그대로 내보낸다. 브라우저가 화면에 띄우도록 inline 으로 준다."""
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", media)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", "inline")
        # 사건 자료다. 어디에도 남기지 않는다.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            return self.handle_api("GET")
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            return self.handle_api("POST")
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)


def main() -> None:
    # 윈도우 기본 콘솔(cp949)은 줄표 같은 문자를 못 찍어 서버가 켜지다 죽는다
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = partial(Handler, directory=str(ROOT))
    # 올린 자료를 받아 엔진을 돌리는 서버라 이 컴퓨터 밖에서는 접속하지 못하게 한다
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        status = ocr_status()
        print(f"http://localhost:{port}  (Ctrl+C to stop)")
        print(f"사건 저장 위치: {CASES_DIR}")
        print("사진 읽기(OCR): " + ("준비됨" if status["ready"] else f"안 됨 — {status['reason']}"))
        httpd.serve_forever()


if __name__ == "__main__":
    main()
