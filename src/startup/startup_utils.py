from src.nasa.nasa_client import *
from src.user_settings import *
from src.utils.cli_commands import handle_global_command, clear_screen
from src.startup.startup_art import *
import random
from src.startup.console import console

from rich.text import Text


def nasa_apods_menu():
    clear_screen()
    flag = True
    while flag:
        header = Text("─────────────────────── ", style="app.secondary")
        header.append("NASA APOD Requests 🌌", style="app.primary")
        header.append(" ───────────────────────", style="app.secondary")
        console.print(header)

        console.print(
            "      Fetch Astronomy Picture of the Day entries from NASA.\n",
            style="body.text"
        )

        line1 = Text("[1] ", style="app.secondary")
        line1.append("Today’s APOD", style="app.primary")
        line1.append("         ", style="body.text")
        line1.append("[3] ", style="app.secondary")
        line1.append("Random APODs", style="app.primary")
        console.print(line1)

        line2 = Text("[2] ", style="app.secondary")
        line2.append("APOD by date", style="app.primary")
        line2.append("         ", style="body.text")
        line2.append("[4] ", style="app.secondary")
        line2.append("Return to Main Menu", style="app.primary")
        console.print(line2)

        console.print()
        console.print("Option: ", style="app.primary", end="")
        raw = input().strip()

        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Input error: Please enter a number from 1 to 4.\n")
            continue
        except Exception as e:
            print(e)
            return

        match user_choice:
            case 1:
                get_todays_apod()
            case 2:
                get_apod_for_specific_day()
            case 3:
                get_random_n_apods()
            case 4:
                flag = False
            case _:
                print("Input error: Please enter a number from 1 to 4.\n")


def output_files_menu():
    clear_screen()
    flag = True
    while flag:
        header = Text("─────────────────────── ", style="app.secondary")
        header.append("Log & File Tools 🗃️", style="app.primary")
        header.append(" ───────────────────────", style="app.secondary")
        console.print(header)

        console.print(
            "               View and manage your saved APOD logs.\n",
            style="body.text"
        )

        line1 = Text("[1] ", style="app.secondary")
        line1.append("View first N entries", style="app.primary")
        line1.append("           ", style="body.text")
        line1.append("[6] ", style="app.secondary")
        line1.append("Show oldest entry (by date)", style="app.primary")
        console.print(line1)

        line2 = Text("[2] ", style="app.secondary")
        line2.append("View last N entries", style="app.primary")
        line2.append("            ", style="body.text")
        line2.append("[7] ", style="app.secondary")
        line2.append("Clear logs (CSV + JSONL)", style="app.primary")
        console.print(line2)

        line3 = Text("[3] ", style="app.secondary")
        line3.append("View all entries", style="app.primary")
        line3.append("               ", style="body.text")
        line3.append("[8] ", style="app.secondary")
        line3.append("Count logged entries", style="app.primary")
        console.print(line3)

        line4 = Text("[4] ", style="app.secondary")
        line4.append("Delete entry by date", style="app.primary")
        line4.append("           ", style="body.text")
        line4.append("[9] ", style="app.secondary")
        line4.append("Return to Main Menu", style="app.primary")
        console.print(line4)

        line5 = Text("[5] ", style="app.secondary")
        line5.append("Show most recent entry (by date)", style="app.primary")
        console.print(line5)

        console.print()
        console.print("Option: ", style="app.primary", end="")
        raw = input().strip()

        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Input error: Please enter a number from 1 to 9.\n")
            continue
        except Exception as e:
            print(e)
            return

        match user_choice:
            case 1:
                show_first_n_json_log_entries()
            case 2:
                show_last_n_json_log_entries()
            case 3:
                show_all_json_entries()
            case 4:
                delete_one_json_entry()
            case 5:
                fetch_most_recent_json_apod()
            case 6:
                fetch_oldest_json_apod()
            case 7:
                if clear_json_output_file() and clear_csv_output_file():
                    print("\nAll log files have been cleared.\n")
            case 8:
                line_count = get_line_count(0)
                print(f"\nTotal logged entries: {line_count}\n")
            case 9:
                flag = False
            case _:
                print("Input error: Please enter a number from 1 to 9.\n")


def user_settings_menu():
    clear_screen()
    flag = True
    while flag:
        # --- Header ---
        header = Text("─────────────────────── ", style="app.secondary")
        header.append("Preferences 📃", style="app.primary")
        header.append(" ───────────────────────", style="app.secondary")
        console.print(header)

        console.print(
            "   Manage how the app behaves after fetching APOD entries.\n",
            style="body.text"
        )

        line1 = Text("[1] ", style="app.secondary")
        line1.append("View settings", style="app.primary")
        line1.append("                  ", style="body.text")
        line1.append("[3] ", style="app.secondary")
        line1.append("Change auto-set-wallpaper setting", style="app.primary")
        console.print(line1)

        line2 = Text("[2] ", style="app.secondary")
        line2.append("Change auto-redirect setting", style="app.primary")
        line2.append("   ", style="body.text")
        line2.append("[4] ", style="app.secondary")
        line2.append("Return to Main Menu", style="app.primary")
        console.print(line2)

        console.print()
        console.print("Option: ", style="app.primary", end="")
        raw = input().strip()


        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Input error: Please enter a number from 1 to 4.\n")
            continue
        except Exception as e:
            print(e)
            return

        match user_choice:
            case 1:
                settings_dict = get_all_user_settings()
                format_all_user_settings(settings_dict)
            case 2:
                update_automatically_redirect_setting()
            case 3:
                update_automatically_set_wallpaper()
            case 4:
                flag = False
            case _:
                print("Input error: Please enter a number from 1 to 4.\n")


def print_box(title: str, lines: list[str], padding_x: int = 2) -> None:
    """
    Prints a clean Unicode box around a section.
    """
    # Compute inner width
    max_line_len = max((len(line) for line in lines), default=0)
    inner_width = max_line_len + (padding_x * 2)

    # Build top border with title
    title_str = f" {title} "
    if len(title_str) > inner_width:
        inner_width = len(title_str)

    # Top
    left_top = "┌"
    right_top = "┐"
    horiz = "─"

    remaining = inner_width - len(title_str)
    left_run = remaining // 2
    right_run = remaining - left_run
    top = f"{left_top}{horiz * left_run}{title_str}{horiz * right_run}{right_top}"

    # Sides of box
    side = "│"
    mid_lines = []
    for line in lines:
        space = inner_width - len(line)
        left_pad = " " * padding_x
        right_pad = " " * (space - padding_x) if space >= padding_x else ""
        if len(line) > inner_width:
            mid_lines.append(f"{side}{left_pad}{line}{side}")
        else:
            mid_lines.append(f"{side}{left_pad}{line}{right_pad}{side}")

    # Bottom
    left_bot = "└"
    right_bot = "┘"
    bottom = f"{left_bot}{horiz * inner_width}{right_bot}"

    print(top)
    for m in mid_lines:
        print(m)
    print(bottom)

def print_startup():
    # Header
    startup_banner1()
    render_random_startup_art()
    console.print()

    # Separator
    console.print("─" * 90, style="app.secondary") # ━
    console.print()

    # Checks
    checks_lines = run_startup_checks()
    print_startup_info_two_column_boxed_right(
        checks_title="STARTUP CHECKS:",
        checks_lines=checks_lines,
        right_title="QUICK INFO:",
        version_str="Version: 1.0.0",
        tips_lines=startup_tips_lines(),
        gap=6,
        padding_x=2,
    )

    # Alternate startup screen version
    # print_box("Startup Checks:", checks_lines)
    # print()
    #
    # print("Version: 1.0.0\n")
    #
    # print("Tips for getting started:")
    # for tip in startup_tips_lines():
    #     print(f"> {tip}")

    console.print()
    console.print("─" * 90, style="app.secondary")
    console.print()


def render_random_startup_art() -> None:
    random_choice = random.randint(1, 9)
    match random_choice:
        case 1:
            render_space_startup_art_1()
        case 2:
            render_spaceship_startup_art_1()
        case 3:
            render_spaceship_startup_art_2()
        case 4:
            render_moon_startup_art_1()
        case 5:
            render_astronaut_startup_art_1()
        case 6:
            render_astronaut_startup_art_2()
        case 7:
            render_alien_startup_art_1()
        case 8:
            render_alien_startup_art_2()
        case 9:
            render_satellite_startup_art1()


def startup_tips_lines() -> list[str]:
    return [
        "Review the README for usage details.",
        "Fetch today's APOD to begin!",
        "Type /help for commands.",
    ]


def run_startup_checks() -> list[str]:
    """
    Returns a list of (label, status) pairs. Status is 'Found' or 'Created'.
    """
    data_dir_status = "Found"
    settings_status = "Found"
    json_status = "Found"
    csv_status = "Found"

    if not check_if_data_exists():
        create_data_directory()
        data_dir_status = "Created"

    if not check_if_user_settings_exist():
        create_user_settings()
        settings_status = "Created"

    if not check_if_json_output_exists():
        create_json_output_file()
        json_status = "Created"

    if not check_if_csv_output_exists():
        create_csv_output_file()
        csv_status = "Created"

    settings_dict = get_all_user_settings()
    automatically_redirect_setting = settings_dict["automatically_redirect"]
    automatically_set_wallpaper_setting = settings_dict["automatically_set_wallpaper"]

    if automatically_redirect_setting == 'yes':
        automatically_redirect_setting_message = f"Auto-open in browser  ✓ ON"
    else:
        automatically_redirect_setting_message = f"Auto-open in browser  X OFF"

    if automatically_set_wallpaper_setting == 'yes':
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    ✓ ON"
    else:
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    X OFF"

    return [
        f"Data directory        ✓ {data_dir_status}",
        f"JSONL log             ✓ {json_status}",
        f"CSV log               ✓ {csv_status}",
        f"User settings         ✓ {settings_status}",
        automatically_redirect_setting_message,
        automatically_set_wallpaper_setting_message,
    ]


def stylize_line(text: Text) -> None:
    """
    Single-pass stylizer for any line in the startup boxes.
    """

    s = text.plain
    if not s:
        return

    border_chars = {"┌", "┐", "└", "┘", "│", "─"}

    def is_boundary(ch: str) -> bool:
        return ch == "" or (not ch.isalnum())

    stripped = s.lstrip()

    if stripped.startswith(("┌", "└")):
        text.stylize("app.primary", 0, len(s))

        for title in (" STARTUP CHECKS: ", " QUICK INFO: "):
            start = s.find(title)
            if start != -1:
                text.stylize("app.primary", start, start + len(title))

    # 2️Style individual characters
    for idx, ch in enumerate(s):
        if ch in border_chars:
            text.stylize("app.primary", idx, idx + 1)
        elif ch == "✓":
            text.stylize("ok", idx, idx + 1)

    # 'X' coloring
    for idx, ch in enumerate(s):
        if ch != "X":
            continue

        left = s[idx - 1] if idx - 1 >= 0 else ""
        right = s[idx + 1] if idx + 1 < len(s) else ""

        if is_boundary(left) and is_boundary(right):
            text.stylize("err", idx, idx + 1)

    # /help highlighting
    start = 0
    while True:
        i = s.find("/help", start)
        if i == -1:
            break
        text.stylize("app.primary", i, i + 5)
        start = i + 5


def print_startup_info_two_column_boxed_right(
    checks_title: str,
    checks_lines: list[str],
    right_title: str,
    version_str: str,
    tips_lines: list[str],
    gap: int = 6,
    padding_x: int = 2,
) -> None:
    """
    Left: checks box.
    Right: boxed panel containing Version + Tips.
    """

    def _build_box_lines(title: str, lines: list[str], padding_x_local: int) -> list[str]:
        max_line_len = max((len(line) for line in lines), default=0)
        inner_width = max_line_len + (padding_x_local * 2)

        title_str = f" {title} "
        if len(title_str) > inner_width:
            inner_width = len(title_str)

        left_top = "┌"
        right_top = "┐"
        horiz = "─"

        remaining = inner_width - len(title_str)
        left_run = remaining // 2
        right_run = remaining - left_run
        top = f"{left_top}{horiz * left_run}{title_str}{horiz * right_run}{right_top}"

        side = "│"
        mid_lines = []
        for line in lines:
            space = inner_width - len(line)
            left_pad = " " * padding_x_local
            right_pad = " " * (space - padding_x_local) if space >= padding_x_local else ""
            if len(line) > inner_width:
                mid_lines.append(f"{side}{left_pad}{line}{side}")
            else:
                mid_lines.append(f"{side}{left_pad}{line}{right_pad}{side}")

        left_bot = "└"
        right_bot = "┘"
        bottom = f"{left_bot}{horiz * inner_width}{right_bot}"

        return [top] + mid_lines + [bottom]

    # Left box
    left_box_lines = _build_box_lines(checks_title, checks_lines, padding_x)

    # Right box
    right_content: list[str] = [version_str, "", "Tips for getting started:"]
    for tip in tips_lines:
        right_content.append(f"> {tip}")

    right_box_lines = _build_box_lines(right_title, right_content, padding_x)

    left_width = len(left_box_lines[0]) if left_box_lines else 0
    right_width = len(right_box_lines[0]) if right_box_lines else 0

    total_rows = max(len(left_box_lines), len(right_box_lines))
    while len(left_box_lines) < total_rows:
        left_box_lines.append(" " * left_width)
    while len(right_box_lines) < total_rows:
        right_box_lines.append(" " * right_width)

    for l, r in zip(left_box_lines, right_box_lines):
        combined = f"{l}{' ' * gap}{r}"
        t = Text(combined, style="body.text")
        stylize_line(t)
        console.print(t)