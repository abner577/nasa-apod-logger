"""WSL wallpaper helpers that bridge Linux paths and Windows APIs via PowerShell."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from rich.text import Text

from src.startup.console import console


def _get_resolution_type() -> str:
    """Return normalized wallpaper mode derived from ``RESOLUTION_TYPE``."""
    return os.getenv("RESOLUTION_TYPE", "fit").strip().lower() or "fit"


def windows_path_to_wsl_path(raw_windows_path: str) -> Path | None:
    """Convert a Windows path string to a WSL path when available."""
    result = subprocess.run(
        ["wslpath", "-u", raw_windows_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    converted = result.stdout.strip()
    if not converted:
        return None

    return Path(converted)


def to_windows_path(local_image_path: Path) -> str | None:
    """Convert a WSL file path to a Windows path string."""
    result = subprocess.run(
        ["wslpath", "-w", str(local_image_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    converted = result.stdout.strip()
    if not converted:
        return None

    return converted


def get_wallpaper_style_values() -> tuple[str, str]:
    """Resolve wallpaper style values from RESOLUTION_TYPE preferences."""
    resolution_type = _get_resolution_type()

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


def apply_wallpaper_style_preferences_wsl(style_values: tuple[str, str]) -> bool:
    """Set wallpaper style registry values through PowerShell when in WSL."""
    wallpaper_style, tile_value = style_values
    script = (
        "$path = 'HKCU:\\Control Panel\\Desktop';"
        f"Set-ItemProperty -Path $path -Name WallpaperStyle -Value '{wallpaper_style}';"
        f"Set-ItemProperty -Path $path -Name TileWallpaper -Value '{tile_value}';"
        "Set-ItemProperty -Path $path -Name JPEGImportQuality -Type DWord -Value 100;"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = Text("Wallpaper style warning: ", style="err")
        msg.append("Unable to apply style preferences through PowerShell.", style="body.text")
        console.print(msg)
        return False

    resolution_x = os.getenv("RESOLUTION_X", "").strip()
    resolution_y = os.getenv("RESOLUTION_Y", "").strip()
    if resolution_x and resolution_y:
        msg = Text("Wallpaper scaling target: ", style="app.secondary")
        msg.append(f"{resolution_x}x{resolution_y}", style="body.text")
        msg.append(" (style applied via RESOLUTION_TYPE).", style="body.text")
        console.print(msg)

    return True


def set_wallpaper_through_wsl(local_image_path: Path) -> bool:
    """Apply wallpaper from WSL by invoking Windows PowerShell commands."""
    windows_path = to_windows_path(local_image_path)
    if windows_path is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to convert Linux path to Windows path in WSL.", style="body.text")
        console.print(msg)
        return False

    style_values = get_wallpaper_style_values()
    if not apply_wallpaper_style_preferences_wsl(style_values):
        return False

    escaped_path = windows_path.replace("'", "''")
    powershell_script = (
        "$code = @'\n"
        "using System.Runtime.InteropServices;\n"
        "public class WinAPI {\n"
        "  [DllImport(\"user32.dll\", SetLastError=true)]\n"
        "  public static extern bool SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);\n"
        "}\n"
        "'@;\n"
        "Add-Type -TypeDefinition $code;\n"
        f"$ok = [WinAPI]::SystemParametersInfo(20, 0, '{escaped_path}', 3);\n"
        "if (-not $ok) { exit 1 }"
    )

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_script],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0
