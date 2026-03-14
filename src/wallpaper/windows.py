"""Windows wallpaper helpers for style and native API application."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

from rich.text import Text

from src.startup.console import console


def set_wallpaper_windows_native(local_image_path: Path) -> bool:
    """Apply wallpaper directly through Win32 APIs when running on Windows."""
    apply_wallpaper_style_preferences()
    success = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(local_image_path), 3)
    if not success:
        error_code = ctypes.GetLastError()
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"Windows error {error_code}.", style="body.text")
        console.print(msg)
        return False

    return True


def apply_wallpaper_style_preferences() -> None:
    """Apply wallpaper scaling style based on environment configuration values."""
    resolution_type = os.getenv("RESOLUTION_TYPE", "fit").strip().lower()
    resolution_x = os.getenv("RESOLUTION_X", "").strip()
    resolution_y = os.getenv("RESOLUTION_Y", "").strip()

    wallpaper_style, tile_value = get_wallpaper_style_values(resolution_type)

    try:
        import winreg

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        with key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, tile_value)
            winreg.SetValueEx(key, "JPEGImportQuality", 0, winreg.REG_DWORD, 100)

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


def get_wallpaper_style_values(resolution_type: str) -> tuple[str, str]:
    """Resolve wallpaper style values from RESOLUTION_TYPE preferences."""
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
    return style_map.get(resolution_type, style_map["fit"])


def get_desktop_resolution_windows() -> tuple[int, int] | None:
    """Return the desktop resolution when running on Windows natively."""
    try:
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
    except OSError:
        return None

    if width <= 0 or height <= 0:
        return None

    return width, height
