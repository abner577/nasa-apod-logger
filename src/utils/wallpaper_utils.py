"""Wallpaper helpers for optional APOD auto-set behavior across operating systems."""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

from rich.text import Text

from src.startup.console import console
from src.utils.apod_media_utils import download_apod_file, get_existing_date_file_path

SPI_SETDESKWALLPAPER = 0x0014
SPI_GETDESKWALLPAPER = 0x0073
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
MAX_WALLPAPER_PATH = 260
WALLPAPER_DEBUG_ENV = "APOD_WALLPAPER_DEBUG"


def maybe_set_apod_wallpaper(apod_data: dict[str, Any], auto_save_enabled: bool, auto_wallpaper_enabled: bool) -> str | None:
    """Set APOD media as wallpaper when both save and wallpaper settings are enabled.

    This helper resolves an APOD file in the user's Downloads folder, downloading
    once when missing, and applies it as wallpaper for the current platform.
    """
    _debug_wallpaper(
        "entry",
        date=str(apod_data.get("date", "")).strip(),
        media_type=str(apod_data.get("media_type", "")).strip().lower(),
        auto_save_enabled=auto_save_enabled,
        auto_wallpaper_enabled=auto_wallpaper_enabled,
    )

    if not auto_save_enabled or not auto_wallpaper_enabled:
        _debug_wallpaper("settings", skipped="true", reason="auto_save_or_wallpaper_disabled")
        return None

    date_value = str(apod_data.get("date", "")).strip()
    if not date_value:
        _debug_wallpaper("settings", skipped="true", reason="missing_date")
        return None

    media_type = str(apod_data.get("media_type", "")).strip().lower()
    if media_type != "image":
        msg = Text("Wallpaper skipped: ", style="err")
        msg.append("APOD media type is not an image.", style="body.text")
        console.print(msg)
        _debug_wallpaper("media_guard", skipped="true", media_type=media_type, reason="not_image")
        return None

    local_file_path = get_existing_date_file_path(date_value)
    _debug_wallpaper("file_resolve", existing_file_found=bool(local_file_path), existing_file_path=local_file_path or "")

    if local_file_path is None:
        local_file_path = download_apod_file(apod_data)
        _debug_wallpaper("download", attempted="true", download_result_path=local_file_path or "")

    if local_file_path is None:
        _debug_wallpaper("result", status="failed", reason="no_local_file_available")
        return None

    success = _set_wallpaper_for_platform(local_file_path)
    if success:
        msg = Text("Wallpaper updated: ", style="ok")
        msg.append(Path(local_file_path).name, style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)
        _debug_wallpaper("result", status="success", file_path=local_file_path)
        return local_file_path

    _debug_wallpaper("result", status="failed", reason="platform_setter_failed", file_path=local_file_path)
    return None


def _set_wallpaper_for_platform(file_path: str) -> bool:
    """Dispatch wallpaper updates to a platform-specific implementation."""
    current_platform = platform.system().lower()
    is_wsl = _is_wsl()
    _debug_wallpaper("platform_dispatch", platform=current_platform, is_wsl=is_wsl)

    if is_wsl:
        msg = Text("Wallpaper skipped: ", style="err")
        msg.append("WSL detected. Linux wallpaper commands do not update the Windows desktop wallpaper.", style="body.text")
        console.print(msg)
        return False

    if current_platform == "windows":
        return _set_wallpaper_windows(file_path)

    if current_platform == "darwin":
        return _set_wallpaper_macos(file_path)

    if current_platform == "linux":
        return _set_wallpaper_linux(file_path)

    msg = Text("Wallpaper skipped: ", style="err")
    msg.append(f"Unsupported OS '{current_platform}'.", style="body.text")
    console.print(msg)
    return False


def _set_wallpaper_windows(file_path: str) -> bool:
    """Set desktop wallpaper on Windows with the SystemParametersInfo API."""
    absolute_path = str(Path(file_path).resolve())

    success = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        absolute_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
    )
    error_code = ctypes.GetLastError()
    _debug_wallpaper("windows_spi_call", target_path=absolute_path, success=bool(success), last_error=error_code)

    if not success:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Windows SystemParametersInfoW returned an error.", style="body.text")
        console.print(msg)
        return False

    expected_path = _normalize_windows_path(absolute_path)
    active_path = _get_current_windows_wallpaper_path()
    normalized_active_path = _normalize_windows_path(active_path) if active_path else ""
    is_match = bool(active_path) and expected_path == normalized_active_path
    _debug_wallpaper(
        "windows_verify",
        expected_path=expected_path,
        active_path=normalized_active_path,
        matches_expected=is_match,
    )

    if is_match:
        return True

    msg = Text("Wallpaper update warning: ", style="err")
    msg.append("Windows accepted the call, but the active wallpaper path did not match the target file.", style="body.text")
    console.print(msg)
    return False


def _set_wallpaper_macos(file_path: str) -> bool:
    """Set desktop wallpaper on macOS using AppleScript."""
    absolute_path = str(Path(file_path).resolve())
    applescript = (
        'tell application "System Events"\n'
        f'  tell every desktop to set picture to POSIX file "{absolute_path}"\n'
        "end tell"
    )

    return _run_wallpaper_command(["osascript", "-e", applescript], "macOS")


def _set_wallpaper_linux(file_path: str) -> bool:
    """Set desktop wallpaper on Linux using common desktop-environment tools."""
    absolute_path = str(Path(file_path).resolve())
    file_uri = f"file://{absolute_path}"

    linux_commands = [
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", file_uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", file_uri],
        ["plasma-apply-wallpaperimage", absolute_path],
        ["feh", "--bg-fill", absolute_path],
        [
            "xfconf-query",
            "-c",
            "xfce4-desktop",
            "-p",
            "/backdrop/screen0/monitor0/image-path",
            "-s",
            absolute_path,
        ],
    ]

    for command in linux_commands:
        if _run_wallpaper_command(command, "Linux", suppress_output=True):
            return True

    msg = Text("Wallpaper update skipped: ", style="err")
    msg.append("No supported Linux wallpaper command was available.", style="body.text")
    console.print(msg)
    return False


def _run_wallpaper_command(command: list[str], system_label: str, suppress_output: bool = False) -> bool:
    """Execute a wallpaper command and return True on success."""
    if not command:
        return False

    if suppress_output:
        stdout_target = subprocess.DEVNULL
        stderr_target = subprocess.DEVNULL
    else:
        stdout_target = subprocess.PIPE
        stderr_target = subprocess.PIPE

    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=stdout_target,
            stderr=stderr_target,
            text=True,
        )
    except FileNotFoundError:
        return False
    except OSError as error:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"{system_label} command error: {error}", style="body.text")
        console.print(msg)
        return False

    if result.returncode == 0:
        return True

    if suppress_output:
        return False

    error_output = (result.stderr or "").strip()
    if not error_output:
        error_output = f"{system_label} wallpaper command exited with code {result.returncode}."

    msg = Text("Wallpaper update failed: ", style="err")
    msg.append(error_output, style="body.text")
    console.print(msg)
    return False


def _is_wsl() -> bool:
    """Return True when running under Windows Subsystem for Linux."""
    try:
        return "microsoft" in platform.release().lower() or "wsl" in platform.release().lower()
    except Exception:
        return False


def _get_current_windows_wallpaper_path() -> str:
    """Read the currently active Windows wallpaper path from user32."""
    buffer = ctypes.create_unicode_buffer(MAX_WALLPAPER_PATH)
    success = ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, MAX_WALLPAPER_PATH, buffer, 0)
    if not success:
        return ""
    return buffer.value.strip()


def _normalize_windows_path(path_value: str) -> str:
    """Normalize Windows paths for robust comparisons."""
    if not path_value:
        return ""
    return os.path.normcase(os.path.normpath(path_value))


def _debug_wallpaper(stage: str, **kwargs: Any) -> None:
    """Print wallpaper debug lines when APOD_WALLPAPER_DEBUG is enabled."""
    debug_enabled = os.getenv(WALLPAPER_DEBUG_ENV, "0").strip().lower() in {"1", "true", "yes", "on"}
    if not debug_enabled:
        return

    parts = [f"{key}={value}" for key, value in kwargs.items()]
    debug_line = f"[WALLPAPER_DEBUG] {stage}"
    if parts:
        debug_line += " | " + " ".join(parts)

    console.print(debug_line)
