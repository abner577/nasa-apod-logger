from pathlib import Path
import csv
from data_storage import DIR_PATH
from src.utils.data_utils import *

HEADERS = {
    "date": "",
    "title": "",
    "url": "",
    "explanation": "",
    "logged_at": "",
}

csv_file_path = f"{DIR_PATH}/data/output.csv"
csv_file_name = "output.csv"

def check_if_csv_output_exists():
    if Path(csv_file_path).exists() and Path(csv_file_path).is_file():
        print(f"File: '{csv_file_name}' at path: '{csv_file_path}' found ✅")
        return True

    print(f"File: '{csv_file_name}' at path: '{csv_file_path}' does not exist ❌. Create it before proceeding...")
    return False


def create_csv_output_file():
    if check_if_csv_output_exists():
        return

    Path(f"{csv_file_path}").touch()
    write_header_to_csv()
    print(f"File: '{csv_file_name}' at path: '{csv_file_path}' created ✅")


def log_data_to_csv(formatted_apod_data):
    if not check_if_csv_output_exists():
        return

    if check_for_duplicate_csv_entries(formatted_apod_data):
        return

    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=formatted_apod_data.keys())
            writer.writerow(formatted_apod_data)
            print(f"Successfully logged data to '{csv_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{csv_file_name}' at path: '{csv_file_path}' ❌")
    except Exception as e:
        print(e)


def check_for_duplicate_csv_entries(formatted_apod_data):
    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
           content = csv.reader(csv_file)

           for row in content:
              if not row or row[0] == 'date':
                  continue

              if row[0] == formatted_apod_data['date']:
                   print(f"APOD with date: '{formatted_apod_data['date']}' found in: '{csv_file_name}'. Not logging again ⛔")
                   return True

    except PermissionError:
        print(f"Dont have permission to read file: '{csv_file_name}' at path: '{csv_file_path}'.")
    except Exception as e:
        print(e)

    return False


def clear_csv_output_file():
    try:
        with open(file=csv_file_path, mode='w', encoding='utf-8') as csv_file:
            print(f"Successfully cleared file: '{csv_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{csv_file_name}' at path: '{csv_file_path}'.")
    except Exception as e:
        print(e)


def delete_csv_output_file():
    Path(f"{csv_file_path}").unlink()
    print(f"File: '{csv_file_name}' at path: '{csv_file_path}' deleted ✅.")


def write_header_to_csv():
    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=HEADERS.keys())
            writer.writeheader()

    except PermissionError:
        print(f"Dont have permission to write to file: '{csv_file_name}' at path: '{csv_file_path}' ❌")
    except Exception as e:
        print(e)

def show_first_n_csv_log_entries(entries_amount):
    if entries_amount < 1:
        print("Amount of entries cannot be less than 1 ❌")
        return

    count = 0

    if not check_if_csv_output_exists():
        return

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)
            for row in content:
                if not row or row[0] == 'date':
                    continue

                count += 1

    except PermissionError:
        print(f"Dont have permission to read file: '{csv_file_name}' at path: '{csv_file_path}'.")
    except Exception as e:
        print(e)

    if entries_amount > count:
        print(f"We only have {count} entries in total. Displaying all the entries that we have...")
        entries_amount = count
    count = 0

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)

            for row in content:
                if not row or row[0] == 'date':
                    continue

                format_raw_csv_entry(row, count)
                count += 1
                if count == entries_amount:
                    break


    except PermissionError:
        print(f"Dont have permission to read file: '{csv_file_name}' at path: '{csv_file_path}'.")
    except Exception as e:
        print(e)


def format_raw_csv_entry(formatted_csv_entry, count):
    print(f"=====================================")
    print(f"Entry #{count + 1} ({formatted_csv_entry[1]}):")
    print(f"Date: {formatted_csv_entry[0]}\n"
          f"Title: {formatted_csv_entry[1]}\n"
          f"Url: {formatted_csv_entry[2]}\n"
          f"Explanation: {formatted_csv_entry[3]}\n"
          f"Logged_At: {formatted_csv_entry[4]}")

show_first_n_csv_log_entries(1)

def fetch_most_recent_csv_apod():
    pass

def fetch_oldest_csv_apod():
    pass

def show_all_csv_entries():
    pass