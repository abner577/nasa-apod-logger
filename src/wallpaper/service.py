"""Cross-platform wallpaper orchestration for APOD image workflows."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sys
import time
from typing import Any

import requests
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.text import Text

from src.startup.console import console
from src.utils.apod_media_utils import (
    get_apod_download_dir,
    get_existing_date_file_path,
    infer_extension,
    resolve_direct_media_url,
)
from src.wallpaper.linux import set_wallpaper_linux
from src.wallpaper.macos import get_desktop_resolution_macos, get_image_resolution_macos, set_wallpaper_macos
from src.wallpaper.windows import get_desktop_resolution_windows, set_wallpaper_windows_native
from src.wallpaper.wsl import (
    get_desktop_resolution_wsl,
    get_image_resolution_wsl,
    is_wsl_environment,
    set_wallpaper_through_wsl,
    windows_path_to_wsl_path,
)


def apply_auto_wallpaper_from_file_path(raw_file_path: str) -> None:
    """Set wallpaper immediately from a user-provided local image file path."""
    cleaned_path = raw_file_path.strip().strip('"').strip("'")
    if not cleaned_path:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("No file path was provided.", style="body.text")
        console.print(msg)
        return

    local_image_path = _resolve_local_image_path(cleaned_path)
    if local_image_path is None:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("Provided file path does not exist.", style="body.text")
        console.print(msg)
        return

    if local_image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("Provided file is not a supported image type.", style="body.text")
        console.print(msg)
        return

    is_windows = os.name == "nt"
    is_macos = sys.platform == "darwin"
    is_wsl = is_wsl_environment()

    success = _apply_local_image_as_wallpaper_with_progress(
        local_image_path,
        is_windows=is_windows,
        is_macos=is_macos,
        is_wsl=is_wsl,
    )
    if success:
        msg = Text("Success: ", style="ok")
        msg.append("Wallpaper was updated to ", style="body.text")
        msg.append(local_image_path.name, style="app.primary")
        msg.append(" ", style="body.text")
        msg.append("✓", style="ok")
        console.print(msg)
    else:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to apply wallpaper through OS-specific APIs.", style="body.text")
        console.print(msg)


def apply_auto_wallpaper_for_single_apod(apod_data: dict[str, Any]) -> None:
    """Download/reuse APOD image in Downloads and apply it as wallpaper."""
    media_type = str(apod_data.get("media_type", "")).strip().lower()
    if media_type != "image":
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("APOD media is video, so wallpaper was not updated.", style="body.text")
        console.print(msg)
        return

    is_windows = os.name == "nt"
    is_macos = sys.platform == "darwin"
    is_wsl = is_wsl_environment()

    date_value = str(apod_data.get("date", "")).strip()
    if not date_value:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("APOD date is missing.", style="body.text")
        console.print(msg)
        return

    local_image_path = _resolve_or_download_image_for_date(apod_data, date_value)
    if local_image_path is None:
        return

    success = _apply_local_image_as_wallpaper_with_progress(
        local_image_path,
        is_windows=is_windows,
        is_macos=is_macos,
        is_wsl=is_wsl,
    )
    if success:
        msg = Text("Success: ", style="ok")
        msg.append("Wallpaper was updated", style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)
    else:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to apply wallpaper through OS-specific APIs.", style="body.text")
        console.print(msg)


def _resolve_local_image_path(raw_path: str) -> Path | None:
    """Resolve a user-provided image path for the current runtime OS."""
    candidate_path = Path(raw_path).expanduser()
    if candidate_path.exists() and candidate_path.is_file():
        return candidate_path

    if candidate_path.is_absolute() and candidate_path.exists() and candidate_path.is_file():
        return candidate_path

    if is_wsl_environment():
        wsl_converted_path = windows_path_to_wsl_path(raw_path)
        if wsl_converted_path is not None and wsl_converted_path.exists() and wsl_converted_path.is_file():
            return wsl_converted_path

    if not candidate_path.is_absolute():
        resolved_path = candidate_path.resolve()
        if resolved_path.exists() and resolved_path.is_file():
            return resolved_path

    return None


def _apply_local_image_as_wallpaper_with_progress(
    local_image_path: Path,
    *,
    is_windows: bool,
    is_macos: bool,
    is_wsl: bool,
) -> bool:
    """Show Rich progress while applying a user-provided local image as wallpaper."""
    progress_total = 100
    progress_cap_while_running = 92
    poll_interval_seconds = 0.1

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            _set_local_image_as_wallpaper,
            local_image_path,
            is_windows=is_windows,
            is_macos=is_macos,
            is_wsl=is_wsl,
        )
        with Progress(
            SpinnerColumn(style="app.primary"),
            TextColumn(
                "[body.text]Setting [/body.text][app.primary]{task.fields[file_name]}[/app.primary]"
                "[body.text] as wallpaper...[/body.text]"
            ),
            BarColumn(bar_width=None, complete_style="app.primary", finished_style="ok"),
            TextColumn("[app.secondary]{task.percentage:>3.0f}%[/app.secondary]"),
            console=console,
            transient=True,
            expand=True,
        ) as progress:
            task_id = progress.add_task("set-wallpaper", total=progress_total, file_name=local_image_path.name)
            started_at = time.perf_counter()
            while not future.done():
                elapsed_seconds = time.perf_counter() - started_at
                estimated_progress = min(progress_cap_while_running, max(1, int(elapsed_seconds * 45)))
                progress.update(task_id, completed=estimated_progress)
                time.sleep(poll_interval_seconds)

            success = future.result()
            progress.update(task_id, completed=progress_total)

        return success


def _set_local_image_as_wallpaper(
    local_image_path: Path,
    *,
    is_windows: bool,
    is_macos: bool,
    is_wsl: bool,
) -> bool:
    """Run the existing wallpaper-setting flow and return whether it succeeded."""
    _desktop_resolution = _get_desktop_resolution(is_windows=is_windows, is_macos=is_macos, is_wsl=is_wsl)
    _image_resolution = _get_image_resolution(local_image_path, is_wsl=is_wsl, is_macos=is_macos)

    if is_windows:
        return set_wallpaper_windows_native(local_image_path)
    if is_macos:
        return set_wallpaper_macos(local_image_path)
    if is_wsl:
        return set_wallpaper_through_wsl(local_image_path, _get_resolution_type())
    return set_wallpaper_linux(local_image_path)


def _resolve_or_download_image_for_date(apod_data: dict[str, Any], date_value: str) -> Path | None:
    """Return an existing image path for an APOD date or download it once."""
    existing_file = get_existing_date_file_path(date_value)
    if existing_file:
        existing_path = Path(existing_file)
        if existing_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}:
            return existing_path

    media_url = resolve_direct_media_url(apod_data)
    if media_url is None:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("No direct image URL was available.", style="body.text")
        console.print(msg)
        return None

    try:
        response = requests.get(media_url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        msg = Text("Auto-wallpaper download failed: ", style="err")
        msg.append(str(error), style="body.text")
        console.print(msg)
        return None

    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if not content_type.startswith("image/"):
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("APOD is not a downloadable image file.", style="body.text")
        console.print(msg)
        return None

    extension = infer_extension(response, media_url)
    file_path = get_apod_download_dir() / f"apod-{date_value}{extension}"

    if file_path.exists():
        msg = Text("Using existing APOD image: ", style="app.secondary")
        msg.append(file_path.name, style="body.text")
        console.print(msg)
        return file_path

    try:
        with open(file_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    output_file.write(chunk)
    except OSError as error:
        msg = Text("Auto-wallpaper save failed: ", style="err")
        msg.append(str(error), style="body.text")
        console.print(msg)
        return None

    msg = Text("Downloaded wallpaper image: ", style="ok")
    msg.append(file_path.name, style="body.text")
    msg.append(" ✓", style="ok")
    console.print(msg)
    return file_path


def _get_resolution_type() -> str:
    """Return normalized wallpaper mode derived from ``RESOLUTION_TYPE``."""
    return os.getenv("RESOLUTION_TYPE", "fit").strip().lower() or "fit"


def _get_desktop_resolution(*, is_windows: bool, is_macos: bool, is_wsl: bool) -> tuple[int, int] | None:
    """Return the primary desktop resolution as ``(width, height)``."""
    if is_windows:
        return get_desktop_resolution_windows()
    if is_macos:
        return get_desktop_resolution_macos()
    if is_wsl:
        return get_desktop_resolution_wsl()
    return None


def _get_image_resolution(local_image_path: Path, *, is_wsl: bool, is_macos: bool) -> tuple[int, int] | None:
    """Return image dimensions using native OS metadata commands."""
    if is_macos:
        return get_image_resolution_macos(local_image_path)
    if is_wsl:
        return get_image_resolution_wsl(local_image_path)
    return None
