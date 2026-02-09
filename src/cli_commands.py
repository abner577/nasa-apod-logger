"""
cli_commands.py

- Global command handling for menu prompts.
- Commands are available across the app.
"""

from __future__ import annotations
import os

from dataclasses import dataclass
from typing import Optional


from src.utils.user_settings import (update_automatically_redirect_setting, update_automatically_set_wallpaper,)

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

    return None


def handle_global_command(raw: str) -> bool:
    """
    Returns True if a command was recognized and handled.
    Returns False if raw is not a command/

    Command effects:
    - --help: clears screen, shows help, waits, clears screen.
    - --readme: opens README_URL in browser.
    - --quit / q: raises SystemExit.
    - --auto-redirect: prompts and updates the setting.
    - --auto-wallpaper: prompts and updates the setting.
    """
    match = parse_global_command(raw)
    if match is None:
        return False

    if match.name == CMD_HELP:
        _show_help_modal()
        return True

    if match.name == CMD_README:
        _open_readme()
        return True

    if match.name == CMD_AUTO_REDIRECT:
        update_automatically_redirect_setting()
        return True

    if match.name == CMD_AUTO_WALLPAPER:
        update_automatically_set_wallpaper()
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
    input("\nPress Enter to return...")
    clear_screen()


def print_help() -> None:
    print("\n============================= HELP MENU ============================\n")
    print("COMMANDS:")
    print("  --help, /help                        Show this help menu")
    print("  --readme, /readme                    Open README in browser")
    print("  --quit, /quit, q                     Exit the application")
    print("  --auto-redirect, /auto-redirect      Change auto-redirect setting")
    print("  --auto-wallpaper, /auto-wallpaper    Change auto-wallpaper setting")

    print("\n====================================================================")