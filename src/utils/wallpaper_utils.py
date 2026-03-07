"""Wallpaper helpers for optional APOD auto-set behavior across operating systems."""

from __future__ import annotations

import ctypes
import platform
import subprocess
from pathlib import Path
from typing import Any

from rich.text import Text

from src.startup.console import console
from src.utils.apod_media_utils import download_apod_file, get_existing_date_file_path


def maybe_set_apod_wallpaper(apod_data: dict[str, Any], auto_save_enabled: bool, auto_wallpaper_enabled: bool) -> str | None:
    """Set APOD media as wallpaper when both save and wallpaper settings are enabled.

    This function first resolves an APOD file inside the user's global Downloads
    folder using the ``apod-yyyy-mm-dd`` naming pattern. If no file exists, it
    downloads the APOD file once and reuses that path. It then attempts to set
    the file as wallpaper on the current platform and returns the local file
    path when available.
    """
    if not auto_save_enabled or not auto_wallpaper_enabled:
        return None

    date_value = str(apod_data.get("date", "")).strip()
    if not date_value:
        return None

    local_file_path = get_existing_date_file_path(date_value)
    if local_file_path is None:
        local_file_path = download_apod_file(apod_data)

    if local_file_path is None:
        return None

    if _set_wallpaper_for_platform(local_file_path):
        msg = Text("Wallpaper updated: ", style="ok")
        msg.append(Path(local_file_path).name, style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)

    return local_file_path


def _set_wallpaper_for_platform(file_path: str) -> bool:
    """Dispatch wallpaper updates to a platform-specific implementation."""
    current_platform = platform.system().lower()

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
    spi_set_desktop_wallpaper = 20
    update_ini_file = 0x01
    send_change = 0x02

    success = ctypes.windll.user32.SystemParametersInfoW(
        spi_set_desktop_wallpaper,
        0,
        absolute_path,
        update_ini_file | send_change,
    )
    if success:
        return True

    msg = Text("Wallpaper update failed: ", style="err")
    msg.append("Windows SystemParametersInfoW returned an error.", style="body.text")
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
