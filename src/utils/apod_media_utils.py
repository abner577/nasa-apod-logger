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
    # Save to the user's system-level Downloads folder (not inside the app data dir).
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
    try:
        return "microsoft" in os.uname().release.lower() or "wsl" in os.uname().release.lower()
    except AttributeError:
        return False


def _windows_profile_to_wsl_path(windows_path: str) -> Path | None:
    cleaned = windows_path.strip().strip('"')
    if not cleaned or ":" not in cleaned:
        return None

    drive, remainder = cleaned.split(":", 1)
    drive = drive.lower()
    remainder = remainder.replace("\\", "/").lstrip("/")
    return Path("/mnt") / drive / remainder


def _resolve_non_windows_downloads_dir() -> Path:
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
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in DIRECT_MEDIA_EXTENSIONS:
        return suffix
    return ""


def resolve_direct_media_url(apod_data: dict) -> str | None:
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
    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type in CONTENT_TYPE_TO_EXT:
        return CONTENT_TYPE_TO_EXT[content_type]

    from_url = _extract_extension_from_url(url)
    if from_url:
        return from_url

    return ".bin"


def build_download_path(date_value: str, extension: str) -> Path:
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
    download_dir = get_apod_download_dir()
    for existing_file in download_dir.glob(f"apod-{date_value}*"):
        if existing_file.is_file():
            return True
    return False


def download_apod_file(apod_data: dict) -> str | None:
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

        msg = Text("Saved media: ", style="ok")
        msg.append(str(file_path), style="app.primary")
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
    if not save_enabled:
        return None
    return download_apod_file(apod_data)
