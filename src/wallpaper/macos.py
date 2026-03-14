"""macOS wallpaper helpers that apply APOD images through NSWorkspace."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from rich.text import Text

from src.startup.console import console


def _get_macos_scaling_mode(mode: str) -> int:
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


def set_wallpaper_macos(local_image_path: Path) -> bool:
    """Apply wallpaper on macOS with NSWorkspace and map Windows-style modes."""
    # Keep Windows/WSL behavior unchanged; macOS should always use a fill effect.
    scaling_mode = _get_macos_scaling_mode("fill")
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
