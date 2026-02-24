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
        line1 = Text("[1] ", style="app.secondary")
        line1.append("Get started", style="app.primary")
        console.print(line1)

        line2 = Text("[Q] ", style="app.secondary")
        line2.append("Quit", style="app.primary")
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

        msg = Text("\nInput error: ", style="err")
        msg.append("Please enter 1 or Q (or type", style="body.text")
        msg.append(" /help", style="app.primary")
        msg.append(").\n", style="body.text")
        console.print(msg)


# Main Menu
flag = True
while flag:
    console.print()

    header = Text("────────────────────── ", style="app.secondary")
    header.append("Main Menu ☄️", style="app.primary")
    header.append(" ──────────────────────", style="app.secondary")

    information_line = Text("     Fetch APODs, manage logs, or update settings.\n", style="body.text")

    console.print(header)
    console.print(information_line)

    increment_launch_count(int(get_launch_count()["launch_count"]))

    line1 = Text("[1] ", style="app.secondary")
    line1.append("Make a NASA APOD Request", style="app.primary")
    line1.append("      ", style="body.text")  # spacing between columns
    line1.append("[3] ", style="app.secondary")
    line1.append("Change Setting", style="app.primary")
    console.print(line1)

    line2 = Text("[2] ", style="app.secondary")
    line2.append("View/Manage saved logs", style="app.primary")
    line2.append("        ", style="body.text")  # spacing between columns
    line2.append("[4] ", style="app.secondary")
    line2.append("Goodbye 👋", style="app.primary")
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
        msg.append("Please enter a number from 1 to 4 (or type", style="body.text")
        msg.append(" /help", style="app.primary")
        msg.append(").\n", style="body.text")
        console.print(msg)

        continue

    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))
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
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter a number from 1 to 4 (or type", style="body.text")
            msg.append(" /help", style="app.primary")
            msg.append(").\n", style="body.text")
            console.print(msg)