"""Windows wallpaper helpers for applying single APOD image entries automatically."""

from __future__ import annotations

import ctypes
import os
import subprocess
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

    is_windows = os.name == "nt"
    is_wsl = _is_wsl_environment()
    if not is_windows and not is_wsl:
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("Wallpaper updates are currently supported on Windows/WSL only.", style="body.text")
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

    desktop_resolution = _get_desktop_resolution(is_windows=is_windows)
    image_resolution = _get_image_resolution(local_image_path, is_wsl=is_wsl)
    prepared_wallpaper_path = _prepare_wallpaper_image_for_desktop(
        local_image_path=local_image_path,
        date_value=date_value,
        desktop_resolution=desktop_resolution,
        image_resolution=image_resolution,
        is_wsl=is_wsl,
    )

    # Uncomment this if you want 'debug' mode for setting image as wallpaper
    # _print_wallpaper_diagnostics(prepared_wallpaper_path, image_resolution, desktop_resolution)

    if is_windows:
        success = _set_wallpaper_windows_native(prepared_wallpaper_path)
    else:
        success = _set_wallpaper_through_wsl(prepared_wallpaper_path)

    if success:
        msg = Text("Success: ", style="ok")
        msg.append("Wallpaper was updated", style="body.text")
        msg.append(" ✓", style="ok")
        console.print(msg)
    else:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to apply wallpaper through Windows APIs.", style="body.text")
        console.print(msg)


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
    resolution_type = os.getenv("RESOLUTION_TYPE", "fit").strip().lower()
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

    wallpaper_style, tile_value = style_map.get(resolution_type, style_map["fit"])

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


def _is_wsl_environment() -> bool:
    """Return ``True`` when running inside Windows Subsystem for Linux."""
    try:
        release = os.uname().release.lower()
        return "microsoft" in release or "wsl" in release
    except AttributeError:
        return False


def _set_wallpaper_windows_native(local_image_path: Path) -> bool:
    """Apply wallpaper directly through Win32 APIs when running on Windows."""
    _apply_wallpaper_style_preferences()
    success = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(local_image_path), 3)
    if not success:
        error_code = ctypes.GetLastError()
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"Windows error {error_code}.", style="body.text")
        console.print(msg)
        return False

    return True


def _set_wallpaper_through_wsl(local_image_path: Path) -> bool:
    """Apply wallpaper from WSL by invoking Windows PowerShell commands."""
    windows_path = _to_windows_path(local_image_path)
    if windows_path is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Unable to convert Linux path to Windows path in WSL.", style="body.text")
        console.print(msg)
        return False

    style_values = _get_wallpaper_style_values()
    if not _apply_wallpaper_style_preferences_wsl(style_values):
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


def _prepare_wallpaper_image_for_desktop(
    *,
    local_image_path: Path,
    date_value: str,
    desktop_resolution: tuple[int, int] | None,
    image_resolution: tuple[int, int] | None,
    is_wsl: bool,
) -> Path:
    """Prepare an APOD image for desktop wallpaper with quality-focused scaling rules."""
    if desktop_resolution is None or image_resolution is None:
        return local_image_path

    desktop_width, desktop_height = desktop_resolution
    image_width, image_height = image_resolution

    if desktop_width <= 0 or desktop_height <= 0 or image_width <= 0 or image_height <= 0:
        return local_image_path

    scale_x = desktop_width / image_width
    scale_y = desktop_height / image_height
    max_upscale_factor = 1.5

    if image_width >= desktop_width and image_height >= desktop_height:
        strategy = "crop_and_downscale"
    else:
        strategy = "capped_upscale"

    output_path = get_apod_download_dir() / f"apod-{date_value}.prepared.jpg"
    if output_path.exists():
        return output_path

    if strategy == "crop_and_downscale":
        target_scale = max(scale_x, scale_y)
    else:
        target_scale = min(max(scale_x, scale_y), max_upscale_factor)

    if not _prepare_wallpaper_with_powershell(
        source_path=local_image_path,
        output_path=output_path,
        desktop_width=desktop_width,
        desktop_height=desktop_height,
        target_scale=target_scale,
        is_wsl=is_wsl,
    ):
        return local_image_path

    msg = Text("Prepared wallpaper image: ", style="ok")
    msg.append(output_path.name, style="body.text")
    msg.append(" ✓", style="ok")
    console.print(msg)
    return output_path


def _prepare_wallpaper_with_powershell(
    *,
    source_path: Path,
    output_path: Path,
    desktop_width: int,
    desktop_height: int,
    target_scale: float,
    is_wsl: bool,
) -> bool:
    """Create a desktop-sized wallpaper image via System.Drawing for better quality control."""
    source_str = str(source_path)
    output_str = str(output_path)

    if is_wsl:
        source_windows = _to_windows_path(source_path)
        output_windows = _to_windows_path(output_path)
        if source_windows is None or output_windows is None:
            return False
        source_str = source_windows
        output_str = output_windows

    escaped_source = source_str.replace("'", "''")
    escaped_output = output_str.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Drawing;"
        f"$srcPath = '{escaped_source}';"
        f"$dstPath = '{escaped_output}';"
        f"$targetWidth = {desktop_width};"
        f"$targetHeight = {desktop_height};"
        f"$scale = [double]{target_scale};"
        "$src = [System.Drawing.Image]::FromFile($srcPath);"
        "$resizedW = [Math]::Max(1, [int]([Math]::Round($src.Width * $scale)));"
        "$resizedH = [Math]::Max(1, [int]([Math]::Round($src.Height * $scale)));"
        "$resized = New-Object System.Drawing.Bitmap($resizedW, $resizedH);"
        "$g = [System.Drawing.Graphics]::FromImage($resized);"
        "$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;"
        "$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality;"
        "$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality;"
        "$g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality;"
        "$g.DrawImage($src, 0, 0, $resizedW, $resizedH);"
        "$g.Dispose();"
        "$canvas = New-Object System.Drawing.Bitmap($targetWidth, $targetHeight);"
        "$canvasGraphics = [System.Drawing.Graphics]::FromImage($canvas);"
        "$canvasGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;"
        "$canvasGraphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality;"
        "$canvasGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality;"
        "$canvasGraphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality;"
        "$canvasGraphics.Clear([System.Drawing.Color]::Black);"
        "$offsetX = [int](($targetWidth - $resizedW) / 2);"
        "$offsetY = [int](($targetHeight - $resizedH) / 2);"
        "$canvasGraphics.DrawImage($resized, $offsetX, $offsetY, $resizedW, $resizedH);"
        "$canvasGraphics.Dispose();"
        "$encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' } | Select-Object -First 1;"
        "$encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1);"
        "$encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]100);"
        "$canvas.Save($dstPath, $encoder, $encoderParams);"
        "$canvas.Dispose();"
        "$resized.Dispose();"
        "$src.Dispose();"
    )

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return True

    msg = Text("Wallpaper preparation warning: ", style="err")
    msg.append("Unable to prepare a desktop-sized image, using original file.", style="body.text")
    console.print(msg)
    return False


def _to_windows_path(local_image_path: Path) -> str | None:
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


def _get_wallpaper_style_values() -> tuple[str, str]:
    """Resolve wallpaper style values from RESOLUTION_TYPE preferences."""
    resolution_type = os.getenv("RESOLUTION_TYPE", "fit").strip().lower()

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


def _apply_wallpaper_style_preferences_wsl(style_values: tuple[str, str]) -> bool:
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


def _get_desktop_resolution(*, is_windows: bool) -> tuple[int, int] | None:
    """Return the primary desktop resolution as ``(width, height)``."""
    if is_windows:
        return _get_desktop_resolution_windows()

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


def _get_image_resolution(local_image_path: Path, *, is_wsl: bool) -> tuple[int, int] | None:
    """Return image dimensions using PowerShell image metadata on Windows/WSL."""
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

    resolution_type = os.getenv("RESOLUTION_TYPE", "fit").strip().lower() or "fit"
    msg = Text("Wallpaper scaling mode: ", style="app.secondary")
    msg.append(
        f"{resolution_type} (default now favors full-image visibility)",
        style="body.text",
    )
    console.print(msg)
