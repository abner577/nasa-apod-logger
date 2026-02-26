"""
nasa_client.py

Handles all interactions with NASA's APOD public API.
Responsible for fetching APOD data and coordinating persistence actions.
"""

import requests
from dotenv import load_dotenv

from src.storage.data_storage import *
from src.storage.csv_storage import *
from src.storage.json_storage import *
from src.utils.browser_utils import *
from src.utils.data_utils import *
from src.utils.apod_media_utils import maybe_download_apod_file
from src.user_settings import *

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

    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}"
    # print(f"[DEBUG] Full_url: {full_url}")
    response = requests.get(full_url)

    if response.status_code == 200:
        msg = Text("\nSuccess: ", style="ok")
        msg.append("Today's APOD was retrieved ", style="body.text")
        msg.append("✓", style="ok")
        msg.append("\n", style="body.text")
        console.print(msg)
        # print("[DEBUG]: HTTP Response = 200")
        apod_raw_data = response.json()

        save_setting = get_automatically_save_apod_files()
        should_save_file = save_setting and save_setting.get("automatically_save_apod_files") == "yes"
        local_file_path = maybe_download_apod_file(apod_raw_data, should_save_file)

        apod_data = format_apod_data(apod_raw_data, local_file_path=local_file_path or "")

        if not check_if_data_exists():
            msg = Text("Data directory not found. Creating it...\n", style="body.text")
            console.print(msg)
            create_data_directory()

        log_data_to_csv(apod_data)
        log_data_to_json(apod_data)

        redirect_url = apod_data['url']
        automatically_redirect_setting = get_automatically_redirect_setting()

        if automatically_redirect_setting['automatically_redirect'] == 'yes':
            console.print()
            take_user_to_browser(redirect_url)
        else:
            link = Text("\nAPOD link: ", style="body.text")
            link.append(redirect_url, style="app.url")
            link.append("\n", style="body.text")
            console.print(link)

    elif response.status_code == 404 or response.status_code == 403:
        msg = Text("\nRequest error: ", style="err")
        msg.append("Verify your API key and try again.", style="body.text")
        console.print(msg)
        return

    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
        msg = Text("\nNASA API error: ", style="err")
        msg.append("Please try again later.", style="body.text")
        console.print(msg)
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

        # Catch non-numeric input here
        try:
            console.print()
            line1 = Text("[1] ", style="app.secondary")
            line1.append("Enter a date", style="app.primary")
            console.print(line1)

            line2 = Text("[2] ", style="app.secondary")
            line2.append("Back", style="app.primary")
            console.print(line2)
            console.print()

            prompt = Text("Option: ", style="app.secondary")
            console.print(prompt, end="")
            user_choice = int(input().strip())

        except ValueError:
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter 1 or 2.", style="body.text")
            console.print(msg)
            continue

        if user_choice != 1 and user_choice != 2:
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter 1 or 2.", style="body.text")
            console.print(msg)
            continue

        match user_choice:
            case 1:
                # Catch non-numeric input here
                try:
                    console.print()
                    console.print(Text("Year (YYYY): ", style="app.secondary"), end="")
                    year = int(input().strip())
                    console.print(Text("Month (MM): ", style="app.secondary"), end="")
                    month = int(input().strip())
                    console.print(Text("Day (DD): ", style="app.secondary"), end="")
                    day = int(input().strip())

                except ValueError:
                    msg = Text("\nInput error: ", style="err")
                    msg.append("Year, month, and day must be numbers.", style="body.text")
                    console.print(msg)
                    continue

                try:
                    date_object = datetime.date(year, month, day)
                except ValueError as e:
                    console.print(Text(str(e), style="err"))
                    continue

                check_result = check_valid_nasa_date(date_object)

                # If an invalid NASA APOD date is entered, try again
                if check_result is not None:
                    msg = Text("\nInput error: ", style="err")
                    msg.append(str(check_result).replace("\nInput error: ", ""), style="body.text")
                    console.print(msg)
                    continue

                if not check_if_data_exists():
                    msg = Text("Data directory not found. Creating it...\n", style="body.text")
                    console.print(msg)
                    create_data_directory()

                # Valid date at this point
                full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&date={date_object}"
                # print(f"\nDEBUG: Fetching APOD for {date_object}...")
                response = requests.get(full_url)

                if response.status_code == 200:
                    msg = Text("\nSuccess: ", style="ok")
                    msg.append("APOD was retrieved ", style="body.text")
                    msg.append("✓", style="ok")
                    msg.append("\n", style="body.text")
                    console.print(msg)
                    # print("[DEBUG]: HTTP Response = 200")
                    apod_raw_data = response.json()

                    save_setting = get_automatically_save_apod_files()
                    should_save_file = save_setting and save_setting.get("automatically_save_apod_files") == "yes"
                    local_file_path = maybe_download_apod_file(apod_raw_data, should_save_file)

                    apod_data = format_apod_data(apod_raw_data, local_file_path=local_file_path or "")

                    log_data_to_csv(apod_data)
                    log_data_to_json(apod_data)

                    redirect_url = apod_data['url']
                    automatically_redirect_setting = get_automatically_redirect_setting()

                    if automatically_redirect_setting['automatically_redirect'] == 'yes':
                        take_user_to_browser(redirect_url)
                    else:
                        link = Text("\nAPOD link: ", style="body.text")
                        link.append(redirect_url, style="app.url")
                        console.print(link)

                elif response.status_code == 404 or response.status_code == 403:
                    msg = Text("\nRequest error: ", style="err")
                    msg.append("Verify your API key and try again.", style="body.text")
                    console.print(msg)

                elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                    msg = Text("\nNASA API error: ", style="err")
                    msg.append("Please try again later.", style="body.text")
                    console.print(msg)

            case 2:
                flag = False
                console.print()


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
            console.print()
            line1 = Text("[1] ", style="app.secondary")
            line1.append("Request Random APODs", style="app.primary")
            console.print(line1)

            line2 = Text("[2] ", style="app.secondary")
            line2.append("Back", style="app.primary")
            console.print(line2)
            console.print()

            console.print(Text("Option: ", style="app.secondary"), end="")
            user_choice = int(input().strip())

            if user_choice != 1 and user_choice != 2:
                msg = Text("\nInput error: ", style="err")
                msg.append("Please enter 1 or 2.", style="body.text")
                console.print(msg)
                continue

            match user_choice:
                case 1:
                    console.print()
                    prompt = Text("How many random APODs should we fetch? ", style="body.text")
                    prompt.append("(1-20):", style="app.primary")
                    console.print(prompt)

                    n = int(input().strip())

                    # Max of 20, because we don't want to open like 100 tabs in the users browser and cause a crash.
                    if not (0 < n <= 20):
                        msg = Text("\nInput error: ", style="err")
                        msg.append("Number of APODs must be between ", style="body.text")
                        msg.append("1", style="app.primary")
                        msg.append(" and ", style="body.text")
                        msg.append("20", style="app.primary")
                        msg.append(".", style="body.text")
                        console.print(msg)
                        continue


                    full_url = f"{BASE_URL}?api_key={NASA_API_KEY}&count={n}"
                    # print(f"[DEBUG]: Fetching {n} random APODs...")
                    # print(f"[DEBUG] Request URL: {full_url}")
                    response = requests.get(full_url)

                    list_of_formatted_apod_entries = []
                    list_of_unformatted_apod_entries = []

                    if response.status_code == 200:
                        msg = Text("\nSuccess: ", style="ok")
                        msg.append(str(n), style="app.primary")
                        msg.append(" Random APODs were retrieved ", style="body.text")
                        msg.append("✓", style="ok")
                        msg.append("\n", style="body.text")
                        console.print(msg)

                        # print("[DEBUG]: HTTP Response = 200")
                        list_of_unformatted_apod_entries = response.json()

                        save_setting = get_automatically_save_apod_files()
                        should_save_file = save_setting and save_setting.get("automatically_save_apod_files") == "yes"

                        for apod in list_of_unformatted_apod_entries:
                            local_file_path = maybe_download_apod_file(apod, should_save_file)
                            apod = format_apod_data(apod, local_file_path=local_file_path or "")
                            list_of_formatted_apod_entries.append(apod)

                        if not check_if_data_exists():
                            msg = Text("Data directory not found. Creating it now...\n", style="body.text")
                            console.print(msg)
                            create_data_directory()

                        log_multiple_csv_entries(list_of_formatted_apod_entries)
                        console.print()
                        log_multiple_json_entries(list_of_formatted_apod_entries)

                        automatically_redirect_setting = get_automatically_redirect_setting()

                        if automatically_redirect_setting['automatically_redirect'] == 'yes':
                            for apod in list_of_formatted_apod_entries:
                                redirect_url = apod['url']
                                take_user_to_browser(redirect_url)
                        else:
                            console.print()
                            for apod in list_of_formatted_apod_entries:
                                link = Text("APOD link: ", style="body.text")
                                link.append(apod["url"], style="app.url")
                                console.print(link)

                    elif response.status_code == 404 or response.status_code == 403:
                        msg = Text("\nRequest error: ", style="err")
                        msg.append("Verify your API key and try again.", style="body.text")
                        console.print(msg)
                        continue

                    elif response.status_code == 500 or response.status_code == 503 or response.status_code == 504:
                        msg = Text("\nNASA API error: ", style="err")
                        msg.append("Please try again later.", style="body.text")
                        console.print(msg)
                        continue

                case 2:
                    flag = False
                    print()

        except ValueError:
            msg = Text("\nInput error: ", style="err")
            msg.append("Please enter a number.", style="body.text")
            console.print(msg)

        except Exception as e:
            msg = Text("\nUnexpected error: ", style="err")
            msg.append("Please try again.", style="body.text")
            console.print(msg)
            console.print(Text(str(e), style="err"))
