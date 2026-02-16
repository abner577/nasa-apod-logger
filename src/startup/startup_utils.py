from src.nasa.nasa_client import *
from src.user_settings import *
from src.utils.cli_commands import handle_global_command, clear_screen
from src.startup.startup_art import *
import random
from src.startup.console import console

from rich.text import Text
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.rule import Rule


def nasa_apods_menu():
    clear_screen()
    flag = True
    while flag:
        print(
            "─────────────────────── NASA APOD Requests 🌌 ───────────────────────\n"
            "     Fetch Astronomy Picture of the Day (APOD) entries from NASA.\n")

        raw = input(
            "[1] Today’s APOD           [3] Random APODs\n"
            "[2] APOD by date           [4] Return to Main Menu\n\n"
            "Option: "
        ).strip()

        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Invalid input: Please enter a number from 1 to 4.\n")
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
                print("Invalid input: Please enter a number from 1 to 4.\n")


def output_files_menu():
    clear_screen()
    flag = True
    while flag:
        print(
            "─────────────────────── Log & File Tools 🗃️ ───────────────────────\n"
            "         View, manage, and maintain your saved APOD logs\n")


        raw = input(
            "[1] View first N entries           [6] Show oldest entry (by date)\n"
            "[2] View last N entries            [7] Clear logs (CSV + JSONL)\n"
            "[3] View all entries               [8] Count logged entries\n"
            "[4] Delete entry by date           [9] Return to Main Menu\n"
            "[5] Show most recent entry (by date)\n\n"
            "Option: "
        ).strip()

        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Invalid input: Please enter a number from 1 to 9.\n")
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
                print("Invalid input: Please enter a number from 1 to 9.\n")


def user_settings_menu():
    clear_screen()
    flag = True
    while flag:
        print(
            "─────────────────────── Preferences 📃 ───────────────────────\n"
            "   Manage how the app behaves after fetching APOD entries.\n")

        raw = input(
            "[1] View settings                  [3] Change auto-set-wallpaper setting\n"
            "[2] Change auto-redirect setting   [4] Return to Main Menu\n\n"
            "Option: "
        ).strip()

        try:
            if handle_global_command(raw):
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        try:
            user_choice = int(raw)
        except ValueError:
            print("Invalid input: Please enter a number from 1 to 4.\n")
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
                print("Invalid input: Please enter a number from 1 to 4.\n")


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
    console.print("─" * 90, style="app.banner") # ━
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
    console.print("─" * 90, style="app.banner")
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
        automatically_redirect_setting_message = f"Auto-open in browser  [✓] ON"
    else:
        automatically_redirect_setting_message = f"Auto-open in browser  [X] OFF"

    if automatically_set_wallpaper_setting == 'yes':
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    [✓] ON"
    else:
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    [X] OFF"

    return [
        f"Data directory        [✓] {data_dir_status}",
        f"JSONL log             [✓] {json_status}",
        f"CSV log               [✓] {csv_status}",
        f"User settings         [✓] {settings_status}",
        automatically_redirect_setting_message,
        automatically_set_wallpaper_setting_message,
    ]


def stylize_all(text: Text) -> None:
    s = text.plain

    # Color [✓] green
    i = 0
    while True:
        i = s.find("[✓]", i)
        if i == -1:
            break
        text.stylize("ok", i, i + 3)
        i += 3

    # Color [X] red
    i = 0
    while True:
        i = s.find("[X]", i)
        if i == -1:
            break
        text.stylize("err", i, i + 3)
        i += 3

    # Bold + purple ONLY for "/help" (exact substring)
    i = 0
    while True:
        i = s.find("/help", i)
        if i == -1:
            break
        text.stylize("inline.help", i, i + 5)
        i += 5


def stylize_vertical_borders(text: Text) -> None:
    # Style ALL border characters '│' on the line
    s = text.plain
    if "│" not in s:
        return

    start = 0
    while True:
        idx = s.find("│", start)
        if idx == -1:
            break
        text.stylize("accent", idx, idx + 1)
        start = idx + 1


def stylize_box_corners(text: Text) -> None:
    s = text.plain
    corners = ("┌", "┐", "└", "┘")
    start = 0
    while True:
        # find the next corner char among the set
        idxs = [(s.find(c, start), c) for c in corners]
        idxs = [(i, c) for (i, c) in idxs if i != -1]
        if not idxs:
            break
        idx, _ = min(idxs, key=lambda x: x[0])
        text.stylize("box.border.v", idx, idx + 1)
        start = idx + 1


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

    # --- Left box ---
    left_box_lines = _build_box_lines(checks_title, checks_lines, padding_x)

    # --- Right box ---
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
        stripped = combined.lstrip()

        # Top/bottom borders (┌ ... ┐) or (└ ... ┘)
        if stripped.startswith(("┌", "└")):
            t = Text(combined, style="accent")

            # Make the titles pop (same text, just styled)
            for title in (" STARTUP CHECKS: ", " QUICK INFO: "):
                start = combined.find(title)
                if start != -1:
                    t.stylize("title", start, start + len(title))

            console.print(t)
            continue

        # Middle box lines (│ ... │)
        if stripped.startswith("│"):
            t = Text(combined, style="box.body")
            stylize_vertical_borders(t)
            stylize_all(t)
            console.print(t)
            continue

        # Spacer rows (padding)
        console.print(combined)