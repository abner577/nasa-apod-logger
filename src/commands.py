"""
commands.py

Main-menu command handling for NASA APOD Logger.

Phase 1 scope:
- Only "global" commands are supported.
- Commands are intended to work ONLY at the Main Menu prompt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os

from src.config import README_URL
from src.utils.browser_utils import take_user_to_browser  # adjust import if your function lives elsewhere


@dataclass(frozen=True)
class CommandResult:
    handled: bool
    should_exit: bool = False
    message: Optional[str] = None


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_help() -> None:
    """
    Print all supported commands
    """
    print(
        "\n======================= HELP MENU =======================\n"
        "\nNote: Commands are accepted ONLY in the Main Menu.\n\n"
        "Global commands:\n"
        "/help      Show this help screen\n"
        "/readme    Open the GitHub README in your browser\n"
        "/quit      Exit the application\n\n"
    )


def handle_main_menu_command(raw: str) -> CommandResult:
    """
    Handle commands that are allowed at the Main Menu prompt.

    Returns:
        CommandResult:
            - handled=False if this isn't a command (caller should treat it as normal menu input)
            - handled=True if command was processed
            - should_exit=True if the caller should exit the app
    """
    if raw is None:
        return CommandResult(handled=False)

    token = raw.strip()
    if not token:
        return CommandResult(handled=False)

    normalized = token.lower()

    # Help
    if normalized in {"/help", "help", "/?"}:
        print_help()
        return CommandResult(handled=True)

    # Readme
    if normalized in {"/readme", "readme"}:
        try:
            take_user_to_browser(README_URL)
        except Exception as e:
            # keep behavior consistent with your app: print the error and continue
            print(f"Could not open README: {e}")
        return CommandResult(handled=True)

    # Quit
    if normalized in {"/quit", "/q", "q", "quit", "exit"}:
        return CommandResult(handled=True, should_exit=True)

    # If it "looks like" a command but isn't recognized, handle it as a command
    if normalized.startswith("/"):
        print("Unknown command. Type /help to see all commands.\n")
        return CommandResult(handled=True)

    # Not a command
    return CommandResult(handled=False)