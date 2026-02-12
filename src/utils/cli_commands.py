"""
cli_commands.py

- Global command handling for menu prompts.
- Commands are available across the app.
"""

from __future__ import annotations
import os

from dataclasses import dataclass
from typing import Optional


from src.user_settings import (update_automatically_redirect_setting, update_automatically_set_wallpaper, get_all_user_settings, format_all_user_settings)

from src.utils.browser_utils import take_user_to_browser
from src.config import README_URL


@dataclass(frozen=True)
class CommandMatch:
    """
    Represents a normalized command and whether it is recognized as a command.
    """
    name: str

CMD_HELP = "help"
CMD_README = "readme"
CMD_QUIT = "quit"
CMD_AUTO_REDIRECT = "auto_redirect"
CMD_AUTO_WALLPAPER = "auto_wallpaper"
CMD_VIEW_SETTINGS = "settings"


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


def _normalize(raw: str) -> str:
    return raw.strip().lower()


def parse_global_command(raw: str) -> Optional[CommandMatch]:
    """
    If raw input matches a global command, return CommandMatch; else None.
    Accepts multiple syntaxes:
      - --help, -help, /help
      - --readme, -readme, /readme
      - --quit, -quit, /quit, q
      - --auto-redirect, --automatically-redirect, /auto-redirect, /automatically-redirect
      - --auto-wallpaper, --automatically-set-wallpaper, /auto-wallpaper, /automatically-set-wallpaper
      - --settings, /settings, -settings
    """
    s = _normalize(raw)
    if not s:
        return None

    if s == "q":
        return CommandMatch(CMD_QUIT)

    # Allow: --cmd, -cmd, /cmd
    if s.startswith("--"):
        token = s[2:]
    elif s.startswith("-"):
        token = s[1:]
    elif s.startswith("/"):
        token = s[1:]
    else:
        return None

    token = token.strip()

    token = token.replace(" ", "-").replace("_", "-")

    if token == "help":
        return CommandMatch(CMD_HELP)

    if token == "readme":
        return CommandMatch(CMD_README)

    if token in ("quit", "q", "exit"):
        return CommandMatch(CMD_QUIT)

    if token in ("auto-redirect", "automatically-redirect"):
        return CommandMatch(CMD_AUTO_REDIRECT)

    if token in ("auto-wallpaper", "automatically-set-wallpaper"):
        return CommandMatch(CMD_AUTO_WALLPAPER)

    if token == "settings":
        return CommandMatch(CMD_VIEW_SETTINGS)

    return None


def handle_global_command(raw: str) -> bool:
    match = parse_global_command(raw)
    if match is None:
        return False

    if match.name == CMD_HELP:
        _show_help_modal()
        return True

    if match.name == CMD_README:
        run_plain_modal(_open_readme)
        return True

    if match.name == CMD_AUTO_REDIRECT:
        def change_auto_redirect():
            update_automatically_redirect_setting()
            print()

            settings_dict = get_all_user_settings()
            format_all_user_settings(settings_dict)

        run_plain_modal(change_auto_redirect)
        return True

    if match.name == CMD_AUTO_WALLPAPER:
        def change_auto_wallpaper():
            update_automatically_set_wallpaper()
            print()

            settings_dict = get_all_user_settings()
            format_all_user_settings(settings_dict)

        run_plain_modal(change_auto_wallpaper)
        return True

    if match.name == CMD_VIEW_SETTINGS:
        def show_settings():
            settings_dict = get_all_user_settings()
            format_all_user_settings(settings_dict)
        run_plain_modal(show_settings)
        return True

    if match.name == CMD_QUIT:
        raise SystemExit

    return False


def _open_readme() -> None:
    try:
        take_user_to_browser(README_URL)
    except Exception as e:
        print(f"\nCould not open README: {e}\n")


def _show_help_modal() -> None:
    clear_screen()
    print_help()
    input("\nPress Enter to return... ")
    clear_screen()


def print_help() -> None:
    print("\n───────────────────────────── HELP MENU ─────────────────────────────\n")
    print("COMMANDS:")
    print("  --help, /help                        Show this help menu")
    print("  --readme, /readme                    Open README in browser")
    print("  --quit, /quit, q                     Exit the application")
    print("  --settings, /settings                View settings configuration")
    print("  --auto-redirect, /auto-redirect      Change auto-redirect setting")
    print("  --auto-wallpaper, /auto-wallpaper    Change auto-wallpaper setting")

    print("\nNOTES:")
    print("  New here? I recommend opening the README before getting started.\n"
          "  It explains how this tool fetches, stores, and manages NASA APOD entries.\n"
          "  Dont forget to check out the Configuration section to learn how to customize behavior!")

    print()
    print("─" * 68)

def run_plain_modal(fn) -> None:
    """
    Clear screen, run fn(), then wait for Enter and clear screen again.
    Use this for commands that should not print into the startup screen scrollback.
    """
    clear_screen()
    try:
        fn()
    finally:
        input("\nPress Enter to return... ")
        clear_screen()