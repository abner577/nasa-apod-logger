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
from src.utils.user_settings import *

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

    print("Fetching today's APOD...")

    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}"
    print(f"[DEBUG] Full_url: {full_url}")
    response = requests.get(full_url)

    if response.status_code == 200:
        print("Success: Today's APOD was retrieved 🚀.\n")
        apod_data = response.json()
        apod_data = format_apod_data(apod_data)


        if not check_if_data_exists():
            print("Data directory not found. Creating it now...\n")
            create_data_directory()

        print("Saving to CSV log... 🗄️")
        log_data_to_csv(apod_data)

        print("Saving to JSONL log... 🗃️")
        log_data_to_json(apod_data)

        redirect_url = apod_data['url']

        if get_user_settings():
            take_user_to_browser(redirect_url)
        else:
            print(f"APOD link: {redirect_url}\n")

    elif response.status_code == 404 or response.status_code == 403:
        print("Request failed: Check your API key and try again.")
        return
    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
        print("NASA API error: Please try again later.")
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

        # Catch non-numeric input here (e.g., "abc")
        try:
            user_choice = int(input("Pick an option (1-2):\n"
                                    "1. Enter a date\n"
                                    "2. Back\n"))
        except ValueError:
            print("Invalid input: Please enter a number (1-2).")
            continue

        if user_choice != 1 and user_choice != 2:
            print("Invalid input: Please enter a number (1-2).")
            continue

        match user_choice:
            case 1:
                # Catch non-numeric input here (e.g., "Jan")
                try:
                    year = int(input("Enter a year (YYYY): "))
                    month = int(input("Enter a month (MM): "))
                    day = int(input("Enter a day (DD): "))
                except ValueError:
                    print("Invalid input: Year, month, and day must be numbers.")
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
                    print('Data directory not found. Creating it now...')
                    create_data_directory()

                # Valid date at this point
                full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&date={date_object}"
                print(f"Fetching APOD for {date_object}...")
                response = requests.get(full_url)

                if response.status_code == 200:
                    print("Success: APOD was retrieved 🚀\n")
                    apod_data = response.json()
                    apod_data = format_apod_data(apod_data)

                    print("Saving to CSV log... 🗄️")
                    log_data_to_csv(apod_data)

                    print("Saving to JSONL log... 🗃️")
                    log_data_to_json(apod_data)

                    redirect_url = apod_data['url']

                    if get_user_settings():
                        take_user_to_browser(redirect_url)
                    else:
                        print(f"APOD link: {redirect_url}\n")

                elif response.status_code == 404 or response.status_code == 403:
                    print("Request failed: Check your API key and try again.")
                elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                    print("NASA API error: Please try again later.")

            case 2:
                print("Returning...")
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
            user_choice = int(input("\nPick an option (1-2):\n"
                                    "1. Request Random APODs\n"
                                    "2. Back\n"))

            if user_choice != 1 and user_choice != 2:
                print("Invalid option: Please enter 1 or 2.")
                continue

            match user_choice:
                case 1:
                    n = int(input('How many random APODs should we fetch? (1-20): \n'))

                    # Max of 20, because we don't want to open like 100 tabs in the users browser and cause a crash.
                    if not (0 < n <= 20):
                        print("Invalid input: Number of APODs must be between 1 and 20.")
                        continue

                    print(f"Fetching {n} random APODs...")

                    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&count={n}"
                    print(f"[DEBUG] Request URL: {full_url}")
                    response = requests.get(full_url)

                    list_of_formatted_apod_entries = []
                    list_of_unformatted_apod_entries = []

                    if response.status_code == 200:
                        print(f"Success: {n} Random APOD entries were retrieved 🚀\n")
                        list_of_unformatted_apod_entries = response.json()
                        for apod in list_of_unformatted_apod_entries:
                            apod = format_apod_data(apod)
                            list_of_formatted_apod_entries.append(apod)

                        if not check_if_data_exists():
                            print("Data directory not found. Creating it now...\n")
                            create_data_directory()

                        print("Saving to CSV log.. 🗄️")
                        log_multiple_csv_entries(list_of_formatted_apod_entries)

                        print("Saving to JSONL log.. 🗃️")
                        log_multiple_json_entries(list_of_formatted_apod_entries)


                        if get_user_settings():
                            print()
                            for apod in list_of_formatted_apod_entries:
                                redirect_url = apod['url']
                                take_user_to_browser(redirect_url)
                        else:
                            print()
                            for apod in list_of_formatted_apod_entries:
                                redirect_url = apod['url']
                                print(f"APOD link: {redirect_url}")

                    elif response.status_code == 404 or response.status_code == 403:
                        print("Request failed: Check your API key and try again.")
                        continue
                    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                        print("NASA API error: Please try again later.")
                        continue

                case 2:
                    print("Returning...")
                    flag = False

        except ValueError:
            print("Invalid input: Please enter a number.")
        except Exception as e:
            print('Unexpected error: Something went wrong. Please try again.')
            print(e)