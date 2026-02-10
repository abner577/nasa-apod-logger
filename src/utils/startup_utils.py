from src.nasa_client import *
from src.utils.user_settings import *
from src.cli_commands import handle_global_command


def nasa_apods_menu():
    flag = True
    while flag:
        print(
            "\n======================= NASA APOD Requests 🌌 =======================\n"
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
            print("Invalid input: Please enter a number from 1 to 4.")
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
                print("\nReturning to Main Menu...")
                flag = False
            case _:
                print("Invalid input: Please enter a number from 1 to 4.")


def output_files_menu():
    flag = True
    while flag:
        print(
            "\n======================= Log & File Tools 🗃️ =======================\n"
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
            print("Invalid input: Please enter a number from 1 to 9 (or type /help).")
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
                print("\nReturning to Main Menu...")
                flag = False
            case _:
                print("Invalid input: Please enter a number from 1 to 9 (or type /help).")


def user_settings_menu():
    flag = True
    while flag:
        print(
            "\n======================= Preferences 📃 =======================\n"
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
            print("Invalid input: Please enter a number from 1 to 4 (or type /help).")
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
                print("\nReturning to Main Menu...")
                flag = False
            case _:
                print("Invalid input: Please enter a number from 1 to 4 (or type /help).")

def print_box(title: str, lines: list[str], padding_x: int = 2) -> None:
    """
    Prints a clean Unicode box around a titled section.
    """
    # Compute inner width: longest line + padding on both sides
    max_line_len = max((len(line) for line in lines), default=0)
    inner_width = max_line_len + (padding_x * 2)

    # Build top border with title
    title_str = f" {title} "
    # Make sure the title fits; if title is longer, expand inner width
    if len(title_str) > inner_width:
        inner_width = len(title_str)

    # Top: ┌─── Title ───┐
    left_top = "┌"
    right_top = "┐"
    horiz = "─"

    # Place title after a run of horizontals
    # Example: ┌──── Startup Checks ────┐
    remaining = inner_width - len(title_str)
    left_run = remaining // 2
    right_run = remaining - left_run
    top = f"{left_top}{horiz * left_run}{title_str}{horiz * right_run}{right_top}"

    # Middle lines: │  ...  │
    side = "│"
    mid_lines = []
    for line in lines:
        space = inner_width - len(line)
        left_pad = " " * padding_x
        right_pad = " " * (space - padding_x) if space >= padding_x else ""
        # If for some reason line is longer than inner_width, don't break; just print it.
        if len(line) > inner_width:
            mid_lines.append(f"{side}{left_pad}{line}{side}")
        else:
            mid_lines.append(f"{side}{left_pad}{line}{right_pad}{side}")

    # Bottom: └────────┘
    left_bot = "└"
    right_bot = "┘"
    bottom = f"{left_bot}{horiz * inner_width}{right_bot}"

    print(top)
    for m in mid_lines:
        print(m)
    print(bottom)
