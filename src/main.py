from src.utils.startup_utils import *
from src.startup_art import *
from src.config import *

"""
main.py

Program entry point.
Responsible for the main menu loop and user interaction flow.
"""

startup_banner2()
render_alien_startup_art_2()
print("\n")
print("-----------------------------------------------------------------------------\n")

# Startup checks (create if missing)
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


checks_lines = [
    f"Data directory     [✓] {data_dir_status}",
    f"JSONL log          [✓] {json_status}",
    f"CSV log            [✓] {csv_status}",
    f"User settings      [✓] {settings_status}",
]

print_box("Startup Checks:", checks_lines)
print("\nVersion: 1.0.0\n")

# Onboarding block (placeholder for now — conditional logic can be added next)
# (Get started with — shown only on first launches)
print("Get started with:")
print("> Fetch today’s APOD")
print("> Fetch an APOD by date")
print("> Browse saved history")
print("> Toggle auto-open setting")

print("\n-------------------------------------------------------------------------------\n")

# Entry Prompt
entry_flag = True
while entry_flag:
    entry_choice = input(
        "[1] Get started\n"
        "[Q] Quit\n\n"
        "Option: "
    ).strip()

    if entry_choice == "1":
        entry_flag = False
    elif entry_choice.lower() == "q":
        print("\nGoodbye 👋")
        exit()
    else:
        print("Invalid input: Please enter 1 or Q.")


# Main Menu
flag = True
while flag:
    print("\n======================= Main Menu ☄️ =======================\n")
    increment_launch_count(int(get_launch_count()['launch_count']))

    try:
        user_choice = int(input(
            "[1] Make a NASA APOD Request\n"
            "[2] View/Manage saved logs\n"
            "[3] Change Setting\n"
            "[4] Goodbye 👋\n\n"
            "Option: "
        ))

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

    except ValueError:
        print("Invalid input: Please enter a number from 1 to 4.")
    except Exception as e:
        print(e)