"""WSL wallpaper helpers that bridge Linux paths and Windows APIs."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

from rich.text import Text

from src.startup.console import console
from src.wallpaper.windows import get_wallpaper_style_values


def is_wsl_environment() -> bool:
    """Return ``True`` when running inside Windows Subsystem for Linux."""
    try:
        release = os.uname().release.lower()
        return "microsoft" in release or "wsl" in release
    except AttributeError:
        return False


def set_wallpaper_through_wsl(local_image_path: Path, resolution_type: str) -> bool:
    """Apply wallpaper from WSL by invoking Windows PowerShell commands."""
    windows_path = to_windows_path(local_image_path)
    if windows_path is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to convert Linux path to Windows path in WSL.", style="body.text")
        console.print(msg)
        return False

    style_values = get_wallpaper_style_values(resolution_type)
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


def get_desktop_resolution_wsl() -> tuple[int, int] | None:
    """Return desktop resolution from WSL through PowerShell and user32 APIs."""
    script = (
        "$code = @'\n"
        "using System.Runtime.InteropServices;\n"
        "public static class User32 {\n"
        "  [DllImport(\"user32.dll\")] public static extern int GetSystemMetrics(int nIndex);\n"
        "}\n"
        "'@;\n"
        "Add-Type -TypeDefinition $code;\n"
        "$w = [User32]::GetSystemMetrics(0);\n"
        "$h = [User32]::GetSystemMetrics(1);\n"
        "Write-Output \"$w,$h\";"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return parse_resolution(result.stdout)


def get_image_resolution_wsl(local_image_path: Path) -> tuple[int, int] | None:
    """Return image dimensions on WSL by querying System.Drawing in PowerShell."""
    windows_path = to_windows_path(local_image_path)
    if windows_path is None:
        return None

    escaped_path = windows_path.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Drawing;"
        f"$img = [System.Drawing.Image]::FromFile('{escaped_path}');"
        "Write-Output \"$($img.Width),$($img.Height)\";"
        "$img.Dispose();"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return parse_resolution(result.stdout)


def parse_resolution(value: str) -> tuple[int, int] | None:
    """Parse resolution text formatted as ``width,height``."""
    cleaned = value.strip()
    if not cleaned:
        return None

    parts = cleaned.split(",", maxsplit=1)
    if len(parts) != 2:
        return None

    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError:
        return None

    if width <= 0 or height <= 0:
        return None

    return width, height
