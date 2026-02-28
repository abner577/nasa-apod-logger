from src.nasa.nasa_client import get_todays_apod, get_apod_for_specific_day, get_random_n_apods
from src.nasa.nasa_date import ask_user_for_date
from src.user_settings import (
    get_all_user_settings,
    check_if_user_settings_exist,
    create_user_settings,
    update_automatically_redirect_setting,
    update_automatically_set_wallpaper,
    update_automatically_save_apod_files_setting, print_settings_box,
)
from src.utils.cli_commands import handle_global_command, clear_screen
from src.startup.startup_art import (
    startup_banner1,
    render_space_startup_art_1,
    render_spaceship_startup_art_1,
    render_spaceship_startup_art_2,
    render_moon_startup_art_1,
    render_astronaut_startup_art_1,
    render_astronaut_startup_art_2,
    render_alien_startup_art_1,
    render_alien_startup_art_2,
    render_satellite_startup_art1,
)
from src.storage.data_storage import check_if_data_exists, create_data_directory
from src.storage.json_storage import (
    show_first_n_json_log_entries,
    show_last_n_json_log_entries,
    show_all_json_entries,
    delete_one_json_entry,
    fetch_most_recent_json_apod,
    fetch_oldest_json_apod,
)
from src.storage.csv_storage import delete_one_csv_entry
from src.utils.json_utils import clear_json_output_file, check_if_json_output_exists, create_json_output_file, get_line_count
from src.utils.csv_utils import clear_csv_output_file, check_if_csv_output_exists, create_csv_output_file, write_header_to_csv
import random
from src.startup.console import console
from src.utils.box_utils import build_box_lines, stylize_line

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
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter a number from 1 to 4.\n", style="body.text")
            console.print(msg)
            continue

        except Exception as e:
            console.print()
            console.print(Text(str(e), style="err"))
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
                msg = Text("\nInput error: ", style="err")
                msg.append("Please enter a number from 1 to 4.\n", style="body.text")
                console.print(msg)


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
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter a number from 1 to 9.\n", style="body.text")
            console.print(msg)
            continue

        except Exception as e:
            console.print()
            console.print(Text(str(e), style="err"))
            return

        match user_choice:
            case 1:
                show_first_n_json_log_entries()
            case 2:
                show_last_n_json_log_entries()
            case 3:
                show_all_json_entries()
            case 4:
                target_date = ask_user_for_date()

                found_json = delete_one_json_entry(target_date)
                found_csv = delete_one_csv_entry(target_date)

                if found_json and found_csv:
                    msg = Text("\nDeleted entry: ", style="body.text")
                    msg.append(str(target_date), style="app.primary")
                    msg.append(" ", style="body.text")
                    msg.append("✓\n", style="ok")
                    console.print(msg)
                else:
                    msg = Text("\nNo entry found for ", style="body.text")
                    msg.append(str(target_date), style="app.primary")
                    msg.append(" ", style="body.text")
                    msg.append("X\n", style="err")
                    console.print(msg)
            case 5:
                fetch_most_recent_json_apod()
            case 6:
                fetch_oldest_json_apod()
            case 7:
                if clear_json_output_file() and clear_csv_output_file():
                    msg = Text("\nAll log files have been cleared ", style="body.text")
                    msg.append("✓\n", style="ok")
                    console.print(msg)

                    write_header_to_csv()
            case 8:
                line_count = get_line_count(0)

                msg = Text("\nTotal logged entries: ", style="app.secondary")
                msg.append(f"{line_count}", style="app.primary")
                msg.append("\n", style="body.text")

                console.print(msg)
            case 9:
                flag = False
            case _:
                msg = Text("\nInput error: ", style="err")
                msg.append("Please enter a number from 1 to 9.\n", style="body.text")
                console.print(msg)


def user_settings_menu():
    clear_screen()
    flag = True
    while flag:
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
        line1.append("                     ", style="body.text")
        line1.append("[4] ", style="app.secondary")
        line1.append("Change auto-save-apod-files setting", style="app.primary")
        console.print(line1)

        line2 = Text("[2] ", style="app.secondary")
        line2.append("Change auto-redirect setting", style="app.primary")
        line2.append("      ", style="body.text")
        line2.append("[5] ", style="app.secondary")
        line2.append("Return to Main Menu", style="app.primary")
        console.print(line2)

        line3 = Text("[3] ", style="app.secondary")
        line3.append("Change auto-set-wallpaper setting", style="app.primary")
        console.print(line3)

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
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter a number from 1 to 5.\n", style="body.text")
            console.print(msg)
            continue

        except Exception as e:
            console.print()
            console.print(Text(str(e), style="err"))
            return

        match user_choice:
            case 1:
                console.print()
                settings_dict = get_all_user_settings()
                if settings_dict:
                    print_settings_box(settings_dict)
                console.print()
            case 2:
                update_automatically_redirect_setting()
            case 3:
                update_automatically_set_wallpaper()
            case 4:
                update_automatically_save_apod_files_setting()
            case 5:
                flag = False
            case _:
                msg = Text("\nInput error: ", style="err")
                msg.append("Please enter a number from 1 to 5.\n", style="body.text")
                console.print(msg)


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
    automatically_save_apod_files_setting = settings_dict["automatically_save_apod_files"]

    if automatically_redirect_setting == 'yes':
        automatically_redirect_setting_message = f"Auto-open in browser  ✓ ON"
    else:
        automatically_redirect_setting_message = f"Auto-open in browser  X OFF"

    if automatically_set_wallpaper_setting == 'yes':
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    ✓ ON"
    else:
        automatically_set_wallpaper_setting_message = f"Auto-set-wallpaper    X OFF"

    if automatically_save_apod_files_setting == 'yes':
        automatically_save_apod_files_message = f"Auto-save APOD files  ✓ ON"
    else:
        automatically_save_apod_files_message = f"Auto-save APOD files  X OFF"

    return [
        f"Data directory        ✓ {data_dir_status}",
        f"JSONL log             ✓ {json_status}",
        f"CSV log               ✓ {csv_status}",
        f"User settings         ✓ {settings_status}",
        automatically_redirect_setting_message,
        automatically_set_wallpaper_setting_message,
        automatically_save_apod_files_message,
    ]


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

    # Left box
    left_box_lines = build_box_lines(checks_title, checks_lines, padding_x)

    # Right box
    right_content: list[str] = [version_str, "", "Tips for getting started:"]
    for tip in tips_lines:
        right_content.append(f"> {tip}")

    right_box_lines = build_box_lines(right_title, right_content, padding_x)

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
