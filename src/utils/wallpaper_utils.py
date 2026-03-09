"""Windows wallpaper helpers for applying single APOD image entries automatically."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Any

import requests
from rich.text import Text

from src.startup.console import console
from src.utils.apod_media_utils import (
    get_apod_download_dir,
    get_existing_date_file_path,
    infer_extension,
    resolve_direct_media_url,
)


def apply_auto_wallpaper_for_single_apod(apod_data: dict[str, Any]) -> None:
    """Download/reuse an APOD image in Downloads and set it as wallpaper on Windows.

    This helper is intended for *single APOD fetch flows* only. It skips video
    APODs, reuses previously downloaded files named with ``apod-YYYY-MM-DD``,
    and applies wallpaper style preferences before setting the desktop wallpaper.
    """
    media_type = str(apod_data.get("media_type", "")).strip().lower()
    if media_type != "image":
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("APOD media is video, so wallpaper was not updated.", style="body.text")
        console.print(msg)
        return

    if os.name != "nt":
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("Wallpaper updates are currently supported on Windows only.", style="body.text")
        console.print(msg)
        return

    date_value = str(apod_data.get("date", "")).strip()
    if not date_value:
        msg = Text("Auto-wallpaper skipped: ", style="err")
        msg.append("APOD date is missing.", style="body.text")
        console.print(msg)
        return

    local_image_path = _resolve_or_download_image_for_date(apod_data, date_value)
    if local_image_path is None:
        return

    _apply_wallpaper_style_preferences()

    success = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(local_image_path), 3)
    if success:
        msg = Text("Wallpaper updated: ", style="ok")
        msg.append(local_image_path.name, style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)
    else:
        error_code = ctypes.GetLastError()
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"Windows error {error_code}.", style="body.text")
        console.print(msg)


def _resolve_or_download_image_for_date(apod_data: dict[str, Any], date_value: str) -> Path | None:
    """Return an existing image path for an APOD date or download it once."""
    existing_file = get_existing_date_file_path(date_value)
    if existing_file:
        existing_path = Path(existing_file)
        if existing_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}:
            msg = Text("Using existing APOD image: ", style="app.secondary")
            msg.append(existing_path.name, style="body.text")
            console.print(msg)
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


def _apply_wallpaper_style_preferences() -> None:
    """Apply wallpaper scaling style based on environment configuration values."""
    resolution_type = os.getenv("RESOLUTION_TYPE", "largest").strip().lower()
    resolution_x = os.getenv("RESOLUTION_X", "").strip()
    resolution_y = os.getenv("RESOLUTION_Y", "").strip()

    style_map = {
        "default": ("6", "0"),
        "fit": ("6", "0"),
        "largest": ("10", "0"),
        "fill": ("10", "0"),
        "stretch": ("2", "0"),
        "center": ("0", "0"),
        "tile": ("0", "1"),
        "span": ("22", "0"),
    }

    wallpaper_style, tile_value = style_map.get(resolution_type, style_map["largest"])

    try:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        with key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, tile_value)

    except OSError as error:
        msg = Text("Wallpaper style warning: ", style="err")
        msg.append(str(error), style="body.text")
        console.print(msg)
        return

    if resolution_x and resolution_y:
        msg = Text("Wallpaper scaling target: ", style="app.secondary")
        msg.append(f"{resolution_x}x{resolution_y}", style="body.text")
        msg.append(" (style applied via RESOLUTION_TYPE).", style="body.text")
        console.print(msg)
