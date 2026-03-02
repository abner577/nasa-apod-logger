"""APOD media URL resolution and local download path/file helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

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


def download_apod_file(apod_data: dict) -> str | None:
    """Download APOD media to disk and return the saved file path when successful.

    In plain English, this function validates the APOD date, skips duplicate
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
        response = requests.get(media_url, stream=True, timeout=20)
        response.raise_for_status()

        extension = infer_extension(response, media_url)
        file_path = build_download_path(date_value, extension)

        with open(file_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                output_file.write(chunk)

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
