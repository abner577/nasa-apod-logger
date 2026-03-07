"""APOD media URL resolution and local download path/file helpers."""

from __future__ import annotations

import os
import re
import subprocess
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse


import requests
from rich.text import Text

from src.startup.console import console


DIRECT_MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".svg",
    ".mp4", ".mov", ".webm", ".mkv", ".avi", ".mp3", ".wav",
}

CONTENT_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "image/svg+xml": ".svg",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
}


def get_apod_download_dir() -> Path:
    """Return the folder where APOD media files should be saved on this machine.

    In plain terms, this picks the user's Downloads folder in a way that works
    across Windows, Linux/macOS, and WSL environments. It also makes sure the
    folder exists before returning it, so callers can write files immediately.
    """
    # Save to the user's system-level Downloads folder.
    if os.name == "nt":
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            path = Path(user_profile) / "Downloads"
        else:
            path = Path.home() / "Downloads"
    else:
        path = _resolve_non_windows_downloads_dir()

    path.mkdir(parents=True, exist_ok=True)
    return path


def _is_wsl() -> bool:
    """Check whether the app is currently running inside Windows Subsystem for Linux.

    This helps other helpers decide whether they should map Linux paths to the
    underlying Windows user folders so downloaded files appear where the user
    expects them.
    """
    try:
        return "microsoft" in os.uname().release.lower() or "wsl" in os.uname().release.lower()
    except AttributeError:
        return False


def _windows_profile_to_wsl_path(windows_path: str) -> Path | None:
    """Convert a Windows-style profile path into the equivalent WSL filesystem path.

    For example, a profile path like ``C:\\Users\\name`` becomes
    ``/mnt/c/Users/name``. If the incoming value does not look like a usable
    Windows path, the function returns ``None`` so callers can fall back safely.
    """
    cleaned = windows_path.strip().strip('"')
    if not cleaned or ":" not in cleaned:
        return None

    drive, remainder = cleaned.split(":", 1)
    drive = drive.lower()
    remainder = remainder.replace("\\", "/").lstrip("/")
    return Path("/mnt") / drive / remainder


def _resolve_non_windows_downloads_dir() -> Path:
    """Resolve the best Downloads folder path for non-Windows operating systems.

    On normal Linux/macOS, this returns the local home Downloads folder. When
    running in WSL, it tries to find the linked Windows user profile and use the
    Windows Downloads directory so saved APOD files are easy to find in Explorer.
    """
    # If running under WSL, save directly to the Windows user's Downloads folder
    # so files are visible in Explorer.
    if _is_wsl():
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", "echo", "%USERPROFILE%"],
                capture_output=True,
                text=True,
                check=False,
            )
            windows_profile = result.stdout.strip()
            wsl_profile_path = _windows_profile_to_wsl_path(windows_profile)
            if wsl_profile_path is not None:
                return wsl_profile_path / "Downloads"
        except Exception:
            pass

    return Path.home() / "Downloads"


def _extract_extension_from_url(url: str) -> str:
    """Read a media-style file extension from a URL when one is clearly present.

    The function only returns known media extensions that this app supports. If
    the URL does not clearly end in one of those types, it returns an empty
    string so downstream logic can use other ways to infer file type.
    """
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in DIRECT_MEDIA_EXTENSIONS:
        return suffix
    return ""


def resolve_direct_media_url(apod_data: dict) -> str | None:
    """Choose the best downloadable media URL from an APOD API response.

    This prefers URLs that look like direct media files, trying ``hdurl`` first
    and then ``url``. If neither appears to be a direct media file, it still
    falls back to valid HTTP links when possible. If no usable link exists, it
    returns ``None``.
    """
    hdurl = str(apod_data.get("hdurl", "")).strip()
    url = str(apod_data.get("url", "")).strip()

    if hdurl and _extract_extension_from_url(hdurl):
        return hdurl

    if url and _extract_extension_from_url(url):
        return url

    if hdurl.startswith("http://") or hdurl.startswith("https://"):
        return hdurl

    if url.startswith("http://") or url.startswith("https://"):
        return url

    return None


def infer_extension(response: requests.Response, url: str) -> str:
    """Decide which file extension should be used for a downloaded APOD file.

    First, this looks at the server's reported content type because that is
    usually the most reliable signal. If that is missing or unfamiliar, it uses
    the URL extension. If both are unclear, it returns a generic ``.bin``
    extension so the download can still be saved.
    """
    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type in CONTENT_TYPE_TO_EXT:
        return CONTENT_TYPE_TO_EXT[content_type]

    from_url = _extract_extension_from_url(url)
    if from_url:
        return from_url

    return ".bin"


def _normalize_escaped_url(raw_url: str) -> str:
    """Convert escaped URL fragments from HTML/JSON blobs into normal URLs."""
    normalized = raw_url.strip().strip('"\'')
    normalized = normalized.replace("\\/", "/")
    normalized = normalized.replace("\\u0026", "&")
    normalized = normalized.replace("\\u003d", "=")
    normalized = normalized.replace("\\u0025", "%")
    normalized = unescape(normalized)
    return normalized


def _extract_video_url_from_page(page_url: str) -> str | None:
    """Attempt to locate a direct downloadable video URL from an embed page.

    Some APOD video entries point to HTML embed pages (commonly YouTube). In
    those cases, the initial media request downloads page markup instead of the
    actual video stream. This helper scans page content for direct media links
    and returns the first plausible candidate.
    """
    _debug_video(f"Inspecting embed page for direct media URL: {page_url}")

    try:
        page_response = requests.get(page_url, timeout=20)
        page_response.raise_for_status()
    except requests.RequestException as error:
        _debug_video(f"Embed page request failed: {error}")
        return None

    page_content = page_response.text
    _debug_video(
        f"Embed response status={page_response.status_code}, content-type={page_response.headers.get('content-type', '')}"
    )

    direct_media_match = re.search(
        r"https?://[^\s\"'<>]+(?:\.mp4|\.webm|\.mov)(?:\?[^\s\"'<>]*)?",
        page_content,
        flags=re.IGNORECASE,
    )
    if direct_media_match:
        extracted_url = direct_media_match.group(0)
        _debug_video(f"Matched direct media URL from page: {extracted_url[:180]}")
        return extracted_url

    escaped_googlevideo_match = re.search(
        r"https(?::\\/\\/|://)[^\"'\s]+googlevideo\.com[^\"'\s]+",
        page_content,
        flags=re.IGNORECASE,
    )
    if escaped_googlevideo_match:
        normalized = _normalize_escaped_url(escaped_googlevideo_match.group(0))
        normalized = unquote(normalized)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            _debug_video(f"Matched escaped googlevideo URL from page: {normalized[:180]}")
            return normalized

    _debug_video("No direct video URL found in embed page.")
    return None


def _get_content_type(response: requests.Response) -> str:
    """Return a normalized content-type value without parameters."""
    return response.headers.get("content-type", "").split(";")[0].strip().lower()


def _debug_video(message: str) -> None:
    """Emit debug logs for APOD video download troubleshooting.
       Uncomment this to enable debugging."""
    # print(f"[DEBUG_VIDEO] {message}")


def build_download_path(date_value: str, extension: str) -> Path:
    """Build a non-conflicting destination path for a media file download.

    The base file name uses the APOD date. If a file with that name already
    exists, the function appends a numeric suffix (like ``-1``, ``-2``) until it
    finds an available filename.
    """
    base_name = f"apod-{date_value}"
    download_dir = get_apod_download_dir()
    candidate = download_dir / f"{base_name}{extension}"

    if not candidate.exists():
        return candidate

    suffix = 1
    while True:
        collision_candidate = download_dir / f"{base_name}-{suffix}{extension}"
        if not collision_candidate.exists():
            return collision_candidate
        suffix += 1


def check_if_date_file_exists(date_value: str) -> bool:
    """Check whether any previously downloaded file already exists for an APOD date.

    This is used to avoid duplicate saves for the same day. It scans the target
    Downloads directory for files that start with ``apod-<date>`` and returns
    ``True`` as soon as one is found.
    """
    download_dir = get_apod_download_dir()
    for existing_file in download_dir.glob(f"apod-{date_value}*"):
        if existing_file.is_file():
            return True
    return False


def get_existing_date_file_path(date_value: str) -> str | None:
    """Return an existing APOD file path for a date when one is already saved.

    The lookup scans the configured global Downloads directory for files that
    start with ``apod-<date>``. When one or more matches are found, it returns
    the first path in sorted order so the result is deterministic.
    """
    download_dir = get_apod_download_dir()
    matches = sorted(
        existing_file for existing_file in download_dir.glob(f"apod-{date_value}*")
        if existing_file.is_file()
    )
    if not matches:
        return None
    return str(matches[0])


def download_apod_file(apod_data: dict) -> str | None:
    """Download APOD media to disk and return the saved file path when successful.

    This function validates the APOD date, skips duplicate
    date downloads, chooses a media URL, downloads the content in chunks, saves
    the file in Downloads, and prints a clear success or failure message.
    If anything important is missing or fails, it returns ``None``.
    """
    date_value = str(apod_data.get("date", "")).strip()
    if not date_value:
        return None

    if check_if_date_file_exists(date_value):
        msg = Text("Skipped (duplicate file): ", style="app.secondary")
        msg.append(f"apod-{date_value}", style="app.primary")
        msg.append(" already exists in downloads.", style="body.text")
        console.print(msg)
        return None

    media_url = resolve_direct_media_url(apod_data)
    if media_url is None:
        msg = Text("Media save skipped: ", style="err")
        msg.append("No direct media URL was available. Open APOD in browser and save manually.", style="body.text")
        console.print(msg)
        return None

    try:
        media_type = str(apod_data.get("media_type", "")).strip().lower()
        if media_type == "video":
            _debug_video(f"Initial APOD media URL: {media_url}")

        response = requests.get(media_url, stream=True, timeout=20)
        response.raise_for_status()

        extension = infer_extension(response, media_url)

        if media_type == "video":
            _debug_video(
                "Initial response details: "
                f"status={response.status_code}, final_url={response.url}, "
                f"content-type={response.headers.get('content-type', '')}, "
                f"content-length={response.headers.get('content-length', '')}, "
                f"inferred_extension={extension}"
            )

        if extension == ".bin" and media_type == "video":
            _debug_video("Inferred .bin for video APOD. Attempting fallback URL extraction.")
            fallback_video_url = _extract_video_url_from_page(media_url)
            if fallback_video_url:
                response.close()
                media_url = fallback_video_url
                _debug_video(f"Retrying video download with fallback URL: {media_url[:220]}")
                response = requests.get(media_url, stream=True, timeout=20)
                response.raise_for_status()
                extension = infer_extension(response, media_url)
                _debug_video(
                    "Fallback response details: "
                    f"status={response.status_code}, final_url={response.url}, "
                    f"content-type={response.headers.get('content-type', '')}, "
                    f"content-length={response.headers.get('content-length', '')}, "
                    f"inferred_extension={extension}"
                )
            else:
                _debug_video("Fallback URL extraction returned no candidate URL.")

        if media_type == "video":
            content_type = _get_content_type(response)
            if not content_type.startswith("video/"):
                _debug_video(
                    "Skipping save because response is not a direct video stream: "
                    f"content-type={content_type or '<empty>'}, final_url={response.url}"
                )
                msg = Text("Skipped (video APOD): ", style="app.secondary")
                msg.append(
                    "This APOD is a video source, and cannot be automatically downloaded. "
                    "Click ",
                    style="body.text",
                )
                msg.append("'Open APOD media' ", style="app.primary")
                msg.append("in browser and save manually.", style="body.text")
                console.print(msg)
                return None

            if extension == ".bin":
                _debug_video("Video stream detected with ambiguous extension; defaulting to .mp4")
                extension = ".mp4"

        file_path = build_download_path(date_value, extension)

        first_chunk_logged = False
        with open(file_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue

                if media_type == "video" and not first_chunk_logged:
                    hex_preview = chunk[:32].hex()
                    _debug_video(f"First 32 bytes hex preview: {hex_preview}")
                    first_chunk_logged = True

                output_file.write(chunk)

        if media_type == "video" and not first_chunk_logged:
            _debug_video("No data chunks were received while saving video file.")

        msg = Text("Saved file: ", style="app.secondary")
        msg.append(file_path.name, style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)

        return str(file_path)

    except requests.RequestException as e:
        msg = Text("Media save failed: ", style="err")
        msg.append(str(e), style="body.text")
        console.print(msg)

    except OSError as e:
        msg = Text("Media save failed: ", style="err")
        msg.append(str(e), style="body.text")
        console.print(msg)

    return None


def maybe_download_apod_file(apod_data: dict, save_enabled: bool) -> str | None:
    """Conditionally download APOD media based on the current save preference.

    This acts as a small guard: when saving is disabled it immediately returns
    ``None``; when enabled it delegates to ``download_apod_file`` and returns
    that result unchanged.
    """
    if not save_enabled:
        return None
    return download_apod_file(apod_data)
