from src.utils.startup_utils import *

"""
main.py

Program entry point.
Responsible for the main menu loop and user interaction flow.
"""

print('Welcome to the APOD Logger.')
# startup_banner()
# startup_art()

flag = True
while flag:
    print('======================= Main Menu =======================\n')

    try:
        print('Pick an option (1-3):')
        user_choice = int(input("1. Interacting with Nasa APODS menu\n"
                                "2. Interacting with output files menu\n"
                                "3. Change Setting\n"
                                "4. Quit Main Menu\n"))

        match user_choice:
            case 1:
                nasa_apods_menu()

            case 2:
                output_files_menu()

            case 3:
                user_settings_menu()

            case 4:
                print("Exiting...")
                flag = False

    except ValueError:
        print("Please enter a number (1-3).")
    except Exception as e:
        print(e)







