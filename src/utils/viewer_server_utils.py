"""Local HTTP server helpers for APOD viewer pages and save actions."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import requests

from src.config import DATA_DIR
from src.utils.apod_media_utils import infer_extension

_VIEWER_SERVER_HOST = "0.0.0.0"
_VIEWER_SERVER_PORT = 8765

_server_lock = threading.Lock()
_server_started = False


def _safe_viewer_file(file_name: str) -> Path | None:
    """Resolve a viewer HTML file only when the request stays inside the viewer folder.

    This function protects the local server from serving
    random files on disk. It builds a path under ``data/viewer``, verifies the
    final resolved path is still inside that folder, and confirms the target is
    an existing file before returning it. If anything looks unsafe or missing,
    it returns ``None``.
    """
    viewer_dir = (DATA_DIR / "viewer").resolve()
    target_path = (viewer_dir / file_name).resolve()
    try:
        target_path.relative_to(viewer_dir)
    except ValueError:
        return None

    if not target_path.exists() or not target_path.is_file():
        return None
    return target_path


class _ViewerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        """Route each GET request to the correct local viewer endpoint.

        This is the traffic controller for the tiny local
        HTTP server. It checks the incoming URL path and sends viewer-page
        requests to the HTML-serving handler, download requests to the media
        proxy handler, and returns a 404 for everything else.
        """
        parsed_url = urlparse(self.path)

        if parsed_url.path.startswith("/viewer/"):
            self._serve_viewer(parsed_url.path)
            return

        if parsed_url.path == "/download":
            self._serve_download(parsed_url.query)
            return

        self.send_error(404, "Not found")

    def log_message(self, _format: str, *_args) -> None:
        """Silence default request logging from ``BaseHTTPRequestHandler``.

        The built-in handler normally prints every HTTP request to stderr.
        """
        return

    def _serve_viewer(self, path: str) -> None:
        """Serve a saved viewer HTML file for ``/viewer/<file_name>`` requests.

        This extracts the file name from the request path, validates it through
        the safe-path helper, and then sends the file contents back as UTF-8
        HTML. If the file is missing or invalid, it returns a 404 response.
        """
        file_name = unquote(path[len("/viewer/"):]).strip()
        viewer_file = _safe_viewer_file(file_name)
        if viewer_file is None:
            self.send_error(404, "Viewer file not found")
            return

        content = viewer_file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_download(self, query: str) -> None:
        """Fetch APOD media from NASA URLs and stream it as a browser download.

        This endpoint acts like a controlled relay: it
        validates the query parameters, rejects unsafe or malformed inputs,
        downloads the remote media file, infers a reasonable file extension,
        sets download-friendly headers, and streams bytes to the client in
        chunks. If the remote fetch fails, it returns an HTTP error.
        """
        params = parse_qs(query)
        media_url = params.get("media_url", [""])[0].strip()
        date_value = params.get("date", [""])[0].strip()

        if not media_url or not date_value:
            self.send_error(400, "Missing date or media_url")
            return

        if not (media_url.startswith("https://") or media_url.startswith("http://")):
            self.send_error(400, "Invalid media_url")
            return

        safe_date = "".join(ch for ch in date_value if ch.isdigit() or ch == "-")
        if not safe_date:
            safe_date = "unknown-date"

        try:
            response = requests.get(media_url, stream=True, timeout=20)
            response.raise_for_status()
        except requests.RequestException:
            self.send_error(502, "Unable to fetch APOD media")
            return

        extension = infer_extension(response, media_url)
        filename = f"apod-{safe_date}{extension}"

        self.send_response(200)
        self.send_header("Content-Type", response.headers.get("content-type", "application/octet-stream"))
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()

        try:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
        finally:
            response.close()


def start_viewer_server() -> bool:
    """Start the local threaded viewer server once per process.

    This uses a lock and a boolean guard so repeated calls do not create extra
    server instances.
    """
    global _server_started

    with _server_lock:
        if _server_started:
            return True

        try:
            server = ThreadingHTTPServer((_VIEWER_SERVER_HOST, _VIEWER_SERVER_PORT), _ViewerRequestHandler)
        except OSError:
            return False

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        _server_started = True
        return True


def viewer_http_url(file_name: str) -> str:
    """Build the localhost URL that opens a saved viewer HTML file.

    This is a helper that turns a viewer file name
    into the exact ``http://127.0.0.1:<port>/viewer/...`` link the browser can
    open against the local server.
    """
    return f"http://127.0.0.1:{_VIEWER_SERVER_PORT}/viewer/{file_name}"
