"""
cli_commands.py

- Global command handling for menu prompts.
- Commands are available across the app.
"""

from __future__ import annotations
from typing import Any
import os

from dataclasses import dataclass
from typing import Callable, Optional

from src.user_settings import (
    update_automatically_redirect_setting,
    update_automatically_set_wallpaper,
    update_automatically_save_apod_files_setting,
    get_all_user_settings,
    print_settings_box,
)
from src.wallpaper import apply_auto_wallpaper_from_file_path

from src.utils.browser_utils import take_user_to_browser
from src.config import README_URL
from rich.text import Text
from src.startup.console import console


@dataclass(frozen=True)
class CommandMatch:
    """
    Represents a normalized command and whether it is recognized as a command.
    """
    name: str
    argument: str | None = None

CMD_HELP = "help"
CMD_README = "readme"
CMD_QUIT = "quit"
CMD_AUTO_REDIRECT = "auto_redirect"
CMD_AUTO_WALLPAPER = "auto_wallpaper"
CMD_VIEW_SETTINGS = "settings"
CMD_AUTO_SAVE = "auto_save"


def clear_screen() -> None:
    try:
        is_windows = os.name == "nt"
        cmd = "cls" if is_windows else "clear"
        exit_code = os.system(cmd)
        if exit_code != 0:
            # fallback if clear/cls isn't available or fails
            print("\n" * 80)
    except Exception:
        print("\n" * 80)


def parse_global_command(raw: str) -> Optional[CommandMatch]:
    """
    If raw input matches a global command, return CommandMatch; else None.
    Accepts multiple syntaxes:
      - --help, -help, /help
      - --readme, -readme, /readme
      - --quit, -quit, /quit, quit, q
      - --auto-redirect, --automatically-redirect, /auto-redirect, /automatically-redirect
      - --auto-wallpaper, --automatically-set-wallpaper, /auto-wallpaper, /automatically-set-wallpaper
      - --settings, /settings, -settings
      - --auto-save, /auto-save, --automatically-save-apod-files
    """
    original = raw.strip()
    if not original:
        return None

    lowered = original.lower()

    if lowered == "q":
        return CommandMatch(CMD_QUIT)
    elif lowered == "quit":
        return CommandMatch(CMD_QUIT)

    # Allow: --cmd, -cmd, /cmd plus optional argument text.
    if lowered.startswith("--"):
        remainder = original[2:]
    elif lowered.startswith("-"):
        remainder = original[1:]
    elif lowered.startswith("/"):
        remainder = original[1:]
    else:
        return None

    remainder = remainder.strip()
    if not remainder:
        return None

    parts = remainder.split(maxsplit=1)
    token = parts[0].lower().replace("_", "-")
    argument = parts[1].strip() if len(parts) > 1 else None

    token = token.replace(" ", "-")

    if token == "help" and not argument:
        return CommandMatch(CMD_HELP)

    if token == "readme" and not argument:
        return CommandMatch(CMD_README)

    if token in ("quit", "q", "exit") and not argument:
        return CommandMatch(CMD_QUIT)

    if token in ("auto-redirect", "automatically-redirect") and not argument:
        return CommandMatch(CMD_AUTO_REDIRECT)

    if token in ("auto-wallpaper", "automatically-set-wallpaper"):
        return CommandMatch(CMD_AUTO_WALLPAPER, argument=argument)

    if token == "settings" and not argument:
        return CommandMatch(CMD_VIEW_SETTINGS)

    if token in ("auto-save", "automatically-save-apod-files") and not argument:
        return CommandMatch(CMD_AUTO_SAVE)

    return None


def handle_global_command(raw: str) -> bool:
    """Execute a recognized global command and report whether one was handled."""
    match = parse_global_command(raw)
    if match is None:
        return False

    if match.name == CMD_HELP:
        run_plain_modal(print_help)
        return True

    if match.name == CMD_README:
        run_plain_modal(open_readme)
        return True

    if match.name == CMD_AUTO_REDIRECT:
        def change_auto_redirect() -> Any:
            update_automatically_redirect_setting()

            settings_dict = get_all_user_settings()
            if not settings_dict:
                return

            print_settings_box(settings_dict)

        run_plain_modal(change_auto_redirect)
        return True

    if match.name == CMD_AUTO_WALLPAPER:
        if match.argument:
            def set_wallpaper_from_path() -> Any:
                apply_auto_wallpaper_from_file_path(match.argument or "")

            run_plain_modal(set_wallpaper_from_path)
        else:
            def change_auto_wallpaper() -> Any:
                update_automatically_set_wallpaper()

                settings_dict = get_all_user_settings()
                if not settings_dict:
                    return

                print_settings_box(settings_dict)

            run_plain_modal(change_auto_wallpaper)
        return True

    if match.name == CMD_VIEW_SETTINGS:
        run_plain_modal(show_settings_modal)
        return True

    if match.name == CMD_AUTO_SAVE:
        def change_auto_save() -> Any:
            update_automatically_save_apod_files_setting()

            settings_dict = get_all_user_settings()
            if not settings_dict:
                return

            print_settings_box(settings_dict)

        run_plain_modal(change_auto_save)
        return True

    if match.name == CMD_QUIT:
        raise SystemExit

    return False


def open_readme() -> None:
    try:
        take_user_to_browser(README_URL)
    except Exception as e:
        console.print(f"\nCould not open README: {e}\n")


def show_settings_modal() -> None:
    settings_dict = get_all_user_settings()
    if not settings_dict:
        return
    print_settings_box(settings_dict)


def print_help() -> None:
    """Print the global command help menu in a formatted layout."""
    title = Text("\n", style="body.text")
    title.append("───────────────────────────── ", style="app.secondary")
    title.append("HELP MENU", style="app.primary")
    title.append(" ─────────────────────────────\n", style="app.secondary")
    console.print(title)

    console.print(Text("COMMANDS:", style="app.secondary"))
    prefix_note = Text("Note: ", style="body.text")
    prefix_note.append("Commands support --, -, and / prefixes.", style="app.primary")
    console.print(prefix_note)
    console.print()

    # Command rows helper
    def cmd_row(left: str, right: str) -> None:
        row = Text("", style="body.text")
        row.append(left, style="app.primary")
        padding = max(1, 35 - len(left))
        row.append(" " * padding, style="body.text")
        row.append(right, style="body.text")
        console.print(row)

    cmd_row("--help", "Show this help menu")
    cmd_row("--readme", "Open README in browser")
    cmd_row("--quit", "Exit the application")
    cmd_row("--settings", "View settings configuration")
    cmd_row("--auto-redirect", "Change auto-redirect setting")
    cmd_row("--auto-wallpaper", "Change auto-wallpaper setting")
    cmd_row("--auto-wallpaper <filepath>", "Set wallpaper from a global image path")
    cmd_row("--auto-save", "Change auto-save APOD files setting")

    console.print()

    console.print(Text("NOTES:", style="app.secondary"))

    console.print(Text(
        "New here? I recommend opening the README before getting started.\n"
        "It explains how this tool fetches, stores, and manages NASA APOD entries.\n"
        "Dont forget to check out the Configuration section to learn how to customize behavior!\n",
        style="body.text"
    ))

    console.print(Text("─" * 68, style="app.secondary"))

def run_plain_modal(fn: Optional[Callable[[], None]] = None) -> None:
    """
    Clear screen, run fn() (if provided), then wait for Enter and clear screen again.
    """
    clear_screen()
    try:
        if fn is not None:
            fn()
    finally:
        prompt = Text("\nPress ", style="body.text")
        prompt.append("Enter", style="app.primary")
        prompt.append(" to return... ", style="body.text")

        console.print(prompt)
        input()
        clear_screen()
