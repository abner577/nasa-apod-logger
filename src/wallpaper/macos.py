"""macOS wallpaper helpers using osascript and AppKit APIs."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

from rich.text import Text

from src.startup.console import console


def set_wallpaper_macos(local_image_path: Path) -> bool:
    """Apply wallpaper on macOS with NSWorkspace and map Windows-style modes."""
    # Keep Windows/WSL behavior unchanged; macOS should always use a fill effect.
    scaling_mode = get_macos_scaling_mode("fill")
    allow_clipping = "true"
    escaped_path = str(local_image_path).replace("\\", "\\\\").replace('"', '\\"')

    script = f"""
ObjC.import('AppKit');
ObjC.import('Foundation');

const wallpaperPath = \"{escaped_path}\";
const wallpaperURL = $.NSURL.fileURLWithPath(wallpaperPath);
const screens = $.NSScreen.screens;
const ws = $.NSWorkspace.sharedWorkspace;

const options = $.NSMutableDictionary.dictionary;
options.setObjectForKey($({scaling_mode}), $.NSWorkspaceDesktopImageScalingKey);
options.setObjectForKey($({allow_clipping}), $.NSWorkspaceDesktopImageAllowClippingKey);

for (let i = 0; i < screens.count; i += 1) {{
    const screen = screens.objectAtIndex(i);
    const errorRef = Ref();
    const ok = ws.setDesktopImageURLForScreenOptionsError(wallpaperURL, screen, options, errorRef);
    if (!ok) {{
        $.NSFileHandle.fileHandleWithStandardError.writeData(
            $(\"Failed to set wallpaper for one or more screens.\").dataUsingEncoding($.NSUTF8StringEncoding),
        );
        $.exit(1);
    }}
}}
"""

    result = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False

    resolution_x = os.getenv("RESOLUTION_X", "").strip()
    resolution_y = os.getenv("RESOLUTION_Y", "").strip()
    if resolution_x and resolution_y:
        msg = Text("Wallpaper scaling target: ", style="app.secondary")
        msg.append(f"{resolution_x}x{resolution_y}", style="body.text")
        msg.append(" (style applied via RESOLUTION_TYPE).", style="body.text")
        console.print(msg)

    return True


def get_macos_scaling_mode(mode: str) -> int:
    """Map Windows-compatible wallpaper modes to macOS scaling constants."""
    mode_map = {
        "default": 3,
        "fit": 3,
        "largest": 3,
        "fill": 3,
        "stretch": 1,
        "center": 2,
        "tile": 2,
        "span": 3,
    }
    return mode_map.get(mode, 3)


def get_desktop_resolution_macos() -> tuple[int, int] | None:
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

    return parse_resolution(result.stdout)


def get_image_resolution_macos(local_image_path: Path) -> tuple[int, int] | None:
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
