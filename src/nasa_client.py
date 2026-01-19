"""
nasa_client.py

Handles all interactions with NASA's APOD public API.
Responsible for fetching APOD data and coordinating persistence actions.
"""

import requests
import os
from dotenv import load_dotenv

from src.storage.data_storage import *
from src.storage.csv_storage import *
from src.storage.json_storage import *
from src.utils.browser_utils import *
from src.utils.data_utils import *

load_dotenv()

NASA_API_KEY = os.getenv('NASA_API_KEY')
BASE_URL = os.getenv('BASE_URL')


def get_todays_apod():
    """
       Fetch today's Astronomy Picture of the Day (APOD) from NASA's API.

       Retrieves the APOD for the current date, formats the response data,
       ensures the data directory exists, and logs the snapshot to both
       CSV and JSONL storage.

       Returns:
            None:
    """

    print("Getting today's APOD...")

    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}"
    print(f"Full_url: {full_url}")
    response = requests.get(full_url)

    if response.status_code == 200:
        print("Today's apod was successfully retrieved! 🚀\n")
        apod_data = response.json()
        apod_data = format_apod_data(apod_data)


        if not check_if_data_exists():
            print("Data directory doesnt exist ❌ Creating Data Directory...\n")
            create_data_directory()

        print("Writing data to csv... 🗄️")
        log_data_to_csv(apod_data)

        print("Writing to json... 🗃️")
        log_data_to_json(apod_data)

        redirect_url = apod_data['url']
        take_user_to_browser(redirect_url)

    elif response.status_code == 404 or response.status_code == 403:
        print("This is a user error. Check your API key and try again.")
        return
    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
        print("This is a server error. Try again later.")
        return


def get_apod_for_specific_day():
    """
    Fetch the Astronomy Picture of the Day (APOD) for a user-specified date.

    Prompts the user for a year, month, and day, validates the date against
    NASA APOD constraints, retrieves the APOD for that date, and logs the
    snapshot to CSV and JSONL storage.

    Returns:
        None:
    """
    flag = True
    while flag:
        print("\n================== GET APOD MENU 🛰️==================")

        # Catch non-numeric input here (e.g., "abc")
        try:
            user_choice = int(input("Enter (1-2) for one of the options below:\n"
                                    "1. Enter a Date\n"
                                    "2. Exit GET APOD Menu\n"))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if user_choice != 1 and user_choice != 2:
            print("Invalid option entered. Please enter 1 or 2.")
            continue

        match user_choice:
            case 1:
                # Catch non-numeric input here (e.g., "Jan")
                try:
                    year = int(input("Enter a year (YYYY): "))
                    month = int(input("Enter a month (MM): "))
                    day = int(input("Enter a day (DD): "))
                except ValueError:
                    print("Please enter a valid number.")
                    continue

                try:
                    date_object = datetime.date(year, month, day)
                except ValueError as e:
                    print(e)
                    continue

                check_result = check_valid_nasa_date(date_object)

                # If an invalid NASA APOD date is entered, try again
                if check_result is not None:
                    print(check_result)
                    continue

                if not check_if_data_exists():
                    print('Data directory not found. Creating Data Directory...')
                    create_data_directory()

                # Valid date at this point
                full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&date={date_object}"
                print(f"Retrieving {date_object}'s APOD...")
                response = requests.get(full_url)

                if response.status_code == 200:
                    print("APOD was successfully retrieved! 🚀\n")
                    apod_data = response.json()
                    apod_data = format_apod_data(apod_data)

                    print("Writing data to csv... 🗄️")
                    log_data_to_csv(apod_data)

                    print("Writing to json... 🗃️")
                    log_data_to_json(apod_data)

                    redirect_url = apod_data['url']
                    take_user_to_browser(redirect_url)

                elif response.status_code == 404 or response.status_code == 403:
                    print("🚫 This is a user error. Check your API key and try again.")
                elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                    print("⚠️ This is a server error. Try again later.")

            case 2:
                print("Exiting...")
                flag = False


def get_random_n_apods():
    """
    Fetch a user-defined number of random Astronomy Picture of the Day (APOD) entries.

    Intended to prompt the user for a count, retrieve that many random APOD
    entries from NASA's API, and log each snapshot to persistent storage.

    Returns:
        None:
    """
    flag = True
    while flag:
        try:
            print("\n================== GET RANDOM APODS MENU 🛰️==================")
            user_choice = int(input("Enter (1-2) for one of the options below:\n"
                                    "1. Make a request for random APODS\n"
                                    "2. Exit GET random APODS Menu\n"))

            if user_choice != 1 and user_choice != 2:
                print("Invalid option entered. Please enter 1 or 2.")
                continue

            match user_choice:
                case 1:
                    n = int(input('Enter how many random APOD entries to fetch (1-20):\n'))

                    # Max of 20, because we don't want to open like 100 tabs in the users browser and cause a crash.
                    if not (0 < n <= 20):
                        print("Number of APOD entries must be between 1 and 20.")
                        continue

                    print(f"Getting {n} random APODS...")

                    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&count={n}"
                    print(f"Full_url: {full_url}")
                    response = requests.get(full_url)

                    list_of_formatted_apod_entries = []
                    list_of_unformatted_apod_entries = []

                    if response.status_code == 200:
                        print("APOD entries successfully retrieved! 🚀\n")
                        list_of_unformatted_apod_entries = response.json()
                        for apod in list_of_unformatted_apod_entries:
                            apod = format_apod_data(apod)
                            list_of_formatted_apod_entries.append(apod)

                        if not check_if_data_exists():
                            print("Data directory doesnt exist ❌ Creating Data Directory...\n")
                            create_data_directory()

                        print("Writing data to csv... 🗄️")
                        log_multiple_json_entries(list_of_formatted_apod_entries)

                        print("Writing to json... 🗃️")
                        log_multiple_csv_entries(list_of_formatted_apod_entries)

                        # This will get replaced by opening all apods in the users browser
                        # If the user presses yes to be taken to browser
                        for apod in list_of_formatted_apod_entries:
                            redirect_url = apod['url']
                            take_user_to_browser(redirect_url)

                    elif response.status_code == 404 or response.status_code == 403:
                        print("This is a user error. Check your API key and try again.")
                        continue
                    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                        print("This is a server error. Try again later.")
                        continue

                case 2:
                    print("Exiting...")
                    flag = False

        except ValueError:
            print("Please enter a number.")
        except Exception as e:
            print('Something went wrong. Try again.')
            print(e)
