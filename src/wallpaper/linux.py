"""Linux desktop-environment aware wallpaper helpers and command dispatch."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from rich.text import Text

from src.startup.console import console


def _get_resolution_type() -> str:
    """Return normalized wallpaper mode derived from ``RESOLUTION_TYPE``."""
    return os.getenv("RESOLUTION_TYPE", "fit").strip().lower() or "fit"


def detect_linux_desktop_environment() -> str:
    """Detect Linux desktop environment and normalize it to a canonical value."""
    env_candidates = [
        os.getenv("XDG_CURRENT_DESKTOP", ""),
        os.getenv("DESKTOP_SESSION", ""),
        os.getenv("GNOME_DESKTOP_SESSION_ID", ""),
        os.getenv("KDE_FULL_SESSION", ""),
    ]
    combined = ";".join(value.strip().lower() for value in env_candidates if value)

    aliases = {
        "gnome": {"gnome", "ubuntu", "unity", "cinnamon"},
        "kde": {"kde", "plasma"},
        "xfce": {"xfce", "xubuntu", "xfce4"},
        "mate": {"mate"},
        "lxde": {"lxde"},
        "lxqt": {"lxqt"},
    }

    for canonical, names in aliases.items():
        if any(name in combined for name in names):
            return canonical

    return "unknown"


def run_linux_wallpaper_command(command: list[str], *, command_name: str) -> bool:
    """Run Linux wallpaper command and return ``True`` when exit code is zero."""
    executable = command[0]
    available = shutil.which(executable) is not None
    diagnostics = Text("Linux wallpaper diagnostics: ", style="app.secondary")
    diagnostics.append(f"command={command_name}, available={available}", style="body.text")
    console.print(diagnostics)
    if not available:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"Missing required command '{executable}'. Install {command_name}.", style="body.text")
        console.print(msg)
        return False

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return True

    msg = Text("Wallpaper update failed: ", style="err")
    stderr = (result.stderr or "").strip()
    msg.append(
        f"Command '{command_name}' returned code {result.returncode}. {stderr}".strip(),
        style="body.text",
    )
    console.print(msg)
    return False


def _gnome_picture_options_from_resolution_type() -> str:
    """Map ``RESOLUTION_TYPE`` values to GNOME picture options."""
    mapping = {
        "default": "zoom",
        "fit": "zoom",
        "largest": "zoom",
        "fill": "zoom",
        "stretch": "stretched",
        "center": "centered",
        "tile": "wallpaper",
        "span": "spanned",
    }
    return mapping.get(_get_resolution_type(), "zoom")


def _set_wallpaper_linux_gnome(local_image_path: Path) -> bool:
    """Set wallpaper for GNOME-family desktop environments via gsettings."""
    if shutil.which("gsettings") is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Missing required command 'gsettings'. Install gsettings.", style="body.text")
        console.print(msg)
        return False

    file_uri = local_image_path.resolve().as_uri()
    picture_option = _gnome_picture_options_from_resolution_type()
    commands = [
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", file_uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", file_uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-options", picture_option],
    ]

    for command in commands:
        if not run_linux_wallpaper_command(command, command_name="gsettings"):
            return False

    return True


def _set_wallpaper_linux_kde(local_image_path: Path) -> bool:
    """Set wallpaper in KDE Plasma using PlasmaShell DBus JavaScript API."""
    tool = next((name for name in ["qdbus6", "qdbus-qt5", "qdbus"] if shutil.which(name)), None)
    if tool is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Missing qdbus tool. Install qdbus/qdbus-qt5/qdbus6.", style="body.text")
        console.print(msg)
        return False

    escaped = str(local_image_path.resolve()).replace('"', '\\"')
    script = (
        "var allDesktops = desktops();"
        "for (i = 0; i < allDesktops.length; i++) {"
        "d = allDesktops[i];"
        "d.wallpaperPlugin = 'org.kde.image';"
        "d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General'];"
        f"d.writeConfig('Image', 'file://{escaped}');"
        "}"
    )
    command = [tool, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell", "evaluateScript", script]
    return run_linux_wallpaper_command(command, command_name=tool)


def _set_wallpaper_linux_xfce(local_image_path: Path) -> bool:
    """Set wallpaper for XFCE using xfconf-query and refresh xfdesktop if available."""
    if shutil.which("xfconf-query") is None:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("Missing required command 'xfconf-query'. Install xfconf-query.", style="body.text")
        console.print(msg)
        return False

    list_result = subprocess.run(
        ["xfconf-query", "-c", "xfce4-desktop", "-l"],
        capture_output=True,
        text=True,
        check=False,
    )
    properties: list[str] = []
    if list_result.returncode == 0:
        for line in list_result.stdout.splitlines():
            prop = line.strip()
            if prop.endswith("/last-image") or prop.endswith("/image-path"):
                properties.append(prop)

    if not properties:
        properties = [
            "/backdrop/screen0/monitor0/workspace0/last-image",
            "/backdrop/screen0/monitor0/image-path",
        ]

    success = False
    for prop in properties:
        command = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", str(local_image_path.resolve())]
        success = run_linux_wallpaper_command(command, command_name="xfconf-query") or success

    if shutil.which("xfdesktop") is not None:
        subprocess.run(["xfdesktop", "--reload"], capture_output=True, text=True, check=False)

    if not success:
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append("No XFCE backdrop properties were updated.", style="body.text")
        console.print(msg)
    return success


def _set_wallpaper_linux_mate(local_image_path: Path) -> bool:
    """Set wallpaper on MATE desktop using gsettings."""
    command = [
        "gsettings",
        "set",
        "org.mate.background",
        "picture-filename",
        str(local_image_path.resolve()),
    ]
    return run_linux_wallpaper_command(command, command_name="gsettings")


def _set_wallpaper_linux_lxde(local_image_path: Path) -> bool:
    """Set wallpaper on LXDE via pcmanfm in scaled mode."""
    command = [
        "pcmanfm",
        "--set-wallpaper",
        str(local_image_path.resolve()),
        "--wallpaper-mode=scaled",
    ]
    return run_linux_wallpaper_command(command, command_name="pcmanfm")


def _set_wallpaper_linux_lxqt(local_image_path: Path) -> bool:
    """Best-effort wallpaper support for LXQt, otherwise return unsupported."""
    if shutil.which("pcmanfm-qt") is None:
        msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
        msg.append("LXQt wallpaper command not found (pcmanfm-qt).", style="body.text")
        console.print(msg)
        return False

    command = ["pcmanfm-qt", "--set-wallpaper", str(local_image_path.resolve())]
    return run_linux_wallpaper_command(command, command_name="pcmanfm-qt")


def set_wallpaper_linux(local_image_path: Path) -> bool:
    """Apply wallpaper on Linux desktop environments with DE-specific commands."""
    try:
        desktop_environment = detect_linux_desktop_environment()
        msg = Text("Linux wallpaper diagnostics: ", style="app.secondary")
        msg.append(f"detected DE={desktop_environment}", style="body.text")
        console.print(msg)

        handlers = {
            "gnome": _set_wallpaper_linux_gnome,
            "kde": _set_wallpaper_linux_kde,
            "xfce": _set_wallpaper_linux_xfce,
            "mate": _set_wallpaper_linux_mate,
            "lxde": _set_wallpaper_linux_lxde,
            "lxqt": _set_wallpaper_linux_lxqt,
        }
        handler = handlers.get(desktop_environment)
        if handler is None:
            msg = Text("Auto-wallpaper skipped: ", style="app.secondary")
            msg.append(
                f"Unsupported desktop environment '{desktop_environment}'.",
                style="body.text",
            )
            console.print(msg)
            return False

        return handler(local_image_path)
    except Exception as error:  # noqa: BLE001 - ensure Linux branch never crashes the app flow.
        msg = Text("Wallpaper update failed: ", style="err")
        msg.append(f"Linux wallpaper error: {error}", style="body.text")
        console.print(msg)
        return False
