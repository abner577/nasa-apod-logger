from src.utils.startup_utils import *
from src.config import *
from src.cli_commands import handle_global_command

"""
main.py

Program entry point.
Responsible for the main menu loop and user interaction flow.
"""

print_startup()

entry_flag = True
while entry_flag:
    print_startup()

    raw = input(
        "[1] Get started\n"
        "[Q] Quit\n\n"
        "Option: "
    ).strip()

    try:
        if handle_global_command(raw):
            continue
    except SystemExit:
        print("\nGoodbye 👋")
        raise

    if raw == "1":
        entry_flag = False
    else:
        print('Invalid input: Please enter 1 or Q (or type --help).\n')


# Main Menu
flag = True
while flag:
    print("\n======================= Main Menu ☄️ =======================\n")
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
            nasa_apods_menu()
        case 2:
            output_files_menu()
        case 3:
            user_settings_menu()
        case 4:
            print("\nGoodbye 👋")
            flag = False
        case _:
            print("Invalid input: Please enter a number from 1 to 4 (or type --help).\n")