"""Cross-platform wallpaper helpers for applying single APOD image entries automatically."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.text import Text

from src.startup.console import console
from src.wallpaper.linux import (
    detect_linux_desktop_environment as _linux_detect_linux_desktop_environment,
    run_linux_wallpaper_command as _linux_run_linux_wallpaper_command,
    set_wallpaper_linux as _linux_set_wallpaper_linux,
)
from src.wallpaper.macos import set_wallpaper_macos as _macos_set_wallpaper_macos
from src.wallpaper.windows import (
    apply_wallpaper_style_preferences as _windows_apply_wallpaper_style_preferences,
    set_wallpaper_windows_native as _windows_set_wallpaper_windows_native,
)
from src.wallpaper.wsl import (
    apply_wallpaper_style_preferences_wsl as _wsl_apply_wallpaper_style_preferences_wsl,
    get_wallpaper_style_values as _wsl_get_wallpaper_style_values,
    set_wallpaper_through_wsl as _wsl_set_wallpaper_through_wsl,
    to_windows_path as _wsl_to_windows_path,
    windows_path_to_wsl_path as _wsl_windows_path_to_wsl_path,
)
from src.utils.apod_media_utils import (
    get_apod_download_dir,
    get_existing_date_file_path,
    infer_extension,
    resolve_direct_media_url,
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
    is_wsl = _is_wsl_environment()

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



def _resolve_local_image_path(raw_path: str) -> Path | None:
    """Resolve a user-provided image path for the current runtime OS."""
    candidate_path = Path(raw_path).expanduser()
    if candidate_path.exists() and candidate_path.is_file():
        return candidate_path

    if candidate_path.is_absolute() and candidate_path.exists() and candidate_path.is_file():
        return candidate_path

    is_wsl = _is_wsl_environment()
    if is_wsl:
        wsl_converted_path = _windows_path_to_wsl_path(raw_path)
        if wsl_converted_path is not None and wsl_converted_path.exists() and wsl_converted_path.is_file():
            return wsl_converted_path

    if not candidate_path.is_absolute():
        resolved_path = candidate_path.resolve()
        if resolved_path.exists() and resolved_path.is_file():
            return resolved_path

    return None

def apply_auto_wallpaper_for_single_apod(apod_data: dict[str, Any]) -> None:
    """Download/reuse an APOD image in Downloads and set it as wallpaper.

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

    is_windows = os.name == "nt"
    is_macos = sys.platform == "darwin"
    is_wsl = _is_wsl_environment()

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


def _apply_local_image_as_wallpaper(
    local_image_path: Path,
    *,
    is_windows: bool,
    is_macos: bool,
    is_wsl: bool,
) -> None:
    """Apply a local image path as wallpaper with existing platform-specific logic."""
    success = _set_local_image_as_wallpaper(
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
    return

    desktop_resolution = _get_desktop_resolution(is_windows=is_windows, is_macos=is_macos)
    image_resolution = _get_image_resolution(local_image_path, is_wsl=is_wsl, is_macos=is_macos)

    # Uncomment this if you want 'debug' mode for setting image as wallpaper
    # _print_wallpaper_diagnostics(local_image_path, image_resolution, desktop_resolution)

    if is_windows:
        success = _set_wallpaper_windows_native(local_image_path)
    elif is_macos:
        success = _set_wallpaper_macos(local_image_path)
    elif is_wsl:
        success = _set_wallpaper_through_wsl(local_image_path)
    else:
        success = _set_wallpaper_linux(local_image_path)

    if success:
        msg = Text("Success: ", style="ok")
        msg.append("Wallpaper was updated", style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)
    else:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to apply wallpaper through OS-specific APIs.", style="body.text")
        console.print(msg)


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
            task_id = progress.add_task(
                "set-wallpaper",
                total=progress_total,
                file_name=local_image_path.name,
            )
            started_at = time.perf_counter()
            while not future.done():
                elapsed_seconds = time.perf_counter() - started_at
                estimated_progress = min(
                    progress_cap_while_running,
                    max(1, int(elapsed_seconds * 45)),
                )
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
    desktop_resolution = _get_desktop_resolution(is_windows=is_windows, is_macos=is_macos)
    image_resolution = _get_image_resolution(local_image_path, is_wsl=is_wsl, is_macos=is_macos)

    # Uncomment this if you want 'debug' mode for setting image as wallpaper
    # _print_wallpaper_diagnostics(local_image_path, image_resolution, desktop_resolution)

    if is_windows:
        success = _set_wallpaper_windows_native(local_image_path)
    elif is_macos:
        success = _set_wallpaper_macos(local_image_path)
    elif is_wsl:
        success = _set_wallpaper_through_wsl(local_image_path)
    else:
        success = _set_wallpaper_linux(local_image_path)

    return success


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


def _apply_wallpaper_style_preferences() -> None:
    """Apply wallpaper scaling style based on environment configuration values."""
    _windows_apply_wallpaper_style_preferences()


def _get_resolution_type() -> str:
    """Return normalized wallpaper mode derived from ``RESOLUTION_TYPE``."""
    return os.getenv("RESOLUTION_TYPE", "fit").strip().lower() or "fit"


def _detect_linux_desktop_environment() -> str:
    """Detect Linux desktop environment and normalize it to a canonical value."""
    return _linux_detect_linux_desktop_environment()


def _set_wallpaper_linux(local_image_path: Path) -> bool:
    """Apply wallpaper on Linux desktop environments with DE-specific commands."""
    return _linux_set_wallpaper_linux(local_image_path)


def _run_linux_wallpaper_command(command: list[str], *, command_name: str) -> bool:
    """Run Linux wallpaper command and return ``True`` when exit code is zero."""
    return _linux_run_linux_wallpaper_command(command, command_name=command_name)


def _set_wallpaper_windows_native(local_image_path: Path) -> bool:
    """Apply wallpaper directly through Win32 APIs when running on Windows."""
    return _windows_set_wallpaper_windows_native(local_image_path)


def _set_wallpaper_through_wsl(local_image_path: Path) -> bool:
    """Apply wallpaper from WSL by invoking Windows PowerShell commands."""
    return _wsl_set_wallpaper_through_wsl(local_image_path)


def _set_wallpaper_macos(local_image_path: Path) -> bool:
    """Apply wallpaper on macOS with NSWorkspace and map Windows-style modes."""
    return _macos_set_wallpaper_macos(local_image_path)


def _windows_path_to_wsl_path(raw_windows_path: str) -> Path | None:
    """Convert a Windows path string to a WSL path when available."""
    return _wsl_windows_path_to_wsl_path(raw_windows_path)


def _to_windows_path(local_image_path: Path) -> str | None:
    """Convert a WSL file path to a Windows path string."""
    return _wsl_to_windows_path(local_image_path)


def _get_wallpaper_style_values() -> tuple[str, str]:
    """Resolve wallpaper style values from RESOLUTION_TYPE preferences."""
    return _wsl_get_wallpaper_style_values()


def _apply_wallpaper_style_preferences_wsl(style_values: tuple[str, str]) -> bool:
    """Set wallpaper style registry values through PowerShell when in WSL."""
    return _wsl_apply_wallpaper_style_preferences_wsl(style_values)

def _get_desktop_resolution(*, is_windows: bool, is_macos: bool) -> tuple[int, int] | None:
    """Return the primary desktop resolution as ``(width, height)``."""
    if is_windows:
        return _get_desktop_resolution_windows()

    if is_macos:
        return _get_desktop_resolution_macos()

    return _get_desktop_resolution_wsl()


def _get_desktop_resolution_windows() -> tuple[int, int] | None:
    """Return the desktop resolution when running on Windows natively."""
    try:
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
    except OSError:
        return None

    if width <= 0 or height <= 0:
        return None

    return width, height


def _get_desktop_resolution_wsl() -> tuple[int, int] | None:
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

    return _parse_resolution(result.stdout)


def _get_desktop_resolution_macos() -> tuple[int, int] | None:
    """Return desktop resolution on macOS via AppKit/NSScreen."""
    script = (
        "ObjC.import('AppKit');"
        "const frame = $.NSScreen.mainScreen.frame;"
        "console.log(`${Math.round(frame.size.width)},${Math.round(frame.size.height)}`);"
    )
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return _parse_resolution(result.stdout)


def _get_image_resolution(local_image_path: Path, *, is_wsl: bool, is_macos: bool) -> tuple[int, int] | None:
    """Return image dimensions using native OS metadata commands."""
    if is_macos:
        return _get_image_resolution_macos(local_image_path)

    image_path = str(local_image_path)
    if is_wsl:
        windows_path = _to_windows_path(local_image_path)
        if windows_path is None:
            return None
        image_path = windows_path

    escaped_path = image_path.replace("'", "''")
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

    return _parse_resolution(result.stdout)


def _get_image_resolution_macos(local_image_path: Path) -> tuple[int, int] | None:
    """Return image dimensions on macOS via NSImage."""
    escaped_path = str(local_image_path).replace("\\", "\\\\").replace('"', '\\"')
    script = (
        "ObjC.import('AppKit');"
        f"const image = $.NSImage.alloc.initWithContentsOfFile(\"{escaped_path}\");"
        "if (!image) { $.exit(1); }"
        "const size = image.size;"
        "console.log(`${Math.round(size.width)},${Math.round(size.height)}`);"
    )
    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return _parse_resolution(result.stdout)


def _parse_resolution(value: str) -> tuple[int, int] | None:
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


def _print_wallpaper_diagnostics(
    local_image_path: Path,
    image_resolution: tuple[int, int] | None,
    desktop_resolution: tuple[int, int] | None,
) -> None:
    """Print wallpaper sizing diagnostics to help trace scaling and quality decisions."""
    msg = Text("Wallpaper source image: ", style="app.secondary")
    msg.append(local_image_path.name, style="body.text")
    console.print(msg)

    if image_resolution is not None:
        msg = Text("Wallpaper source resolution: ", style="app.secondary")
        msg.append(f"{image_resolution[0]}x{image_resolution[1]}", style="body.text")
        console.print(msg)

    if desktop_resolution is not None:
        msg = Text("Detected desktop resolution: ", style="app.secondary")
        msg.append(f"{desktop_resolution[0]}x{desktop_resolution[1]}", style="body.text")
        console.print(msg)

    resolution_type = _get_resolution_type()
    msg = Text("Wallpaper scaling mode: ", style="app.secondary")
    msg.append(
        f"{resolution_type} (default now favors full-image visibility)",
        style="body.text",
    )
    console.print(msg)
