from src.startup.startup_utils import *
from src.utils.cli_commands import handle_global_command, clear_screen
from rich.text import Text

"""
main.py

Program entry point.
Responsible for the main menu loop and user interaction flow.
"""

entry_flag = True
while entry_flag:
    print_startup()

    while True:
        line1 = Text("[1] Get started", style="body.text")
        line1.stylize("app.secondary", 0, 3)
        console.print(line1)

        line2 = Text("[Q] Quit", style="body.text")
        line2.stylize("app.secondary", 0, 3)
        console.print(line2)
        console.print()
        console.print("Option: ", style="app.primary", end="")
        raw = input().strip()

        try:
            if handle_global_command(raw):
                print_startup()
                continue
        except SystemExit:
            print("\nGoodbye 👋")
            raise

        if raw == "1":
            entry_flag = False
            break

        if raw.lower() == "q":
            print("\nGoodbye 👋")
            raise SystemExit

        print("Invalid input: Please enter 1 or Q (or type --help).\n")


# Main Menu
flag = True
while flag:
    print("────────────────────── Main Menu ☄️ ──────────────────────\n")
    increment_launch_count(int(get_launch_count()["launch_count"]))

    raw = input(
        "[1] Make a NASA APOD Request\n"
        "[2] View/Manage saved logs\n"
        "[3] Change Setting\n"
        "[4] Goodbye 👋\n\n"
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
        continue

    match user_choice:
        case 1:
            clear_screen()
            nasa_apods_menu()
            clear_screen()
        case 2:
            clear_screen()
            output_files_menu()
            clear_screen()
        case 3:
            clear_screen()
            user_settings_menu()
            clear_screen()
        case 4:
            print("\nGoodbye 👋")
            flag = False
        case _:
            print("Invalid input: Please enter a number from 1 to 4 (or type --help).\n")