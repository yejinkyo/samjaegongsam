"""화면 미리보기용 정적 서버.

`python -m http.server` 는 캐시 헤더를 주지 않아서, 브라우저가 고친 HTML·CSS 를
안 받아 오고 옛 화면을 계속 보여 준다. 여기서는 매번 새로 받게 한다.

    python web/serve.py          # 기본 8765
    python web/serve.py 9000
"""

from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        """404 만 남긴다 — 링크가 끊겼는지는 봐야 하고, 200 로그는 시끄럽다."""
        line = fmt % args
        if " 404 " in line or " 500 " in line:
            sys.stderr.write(f"{line}\n")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = partial(NoCacheHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
