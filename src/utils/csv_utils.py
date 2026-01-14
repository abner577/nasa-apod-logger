from pathlib import Path
import csv

DIR_PATH = "C://Users/joser/PycharmProjects/NASA-APOD-Logger"
csv_file_path = f"{DIR_PATH}/data/output.csv"
csv_file_name = "output.csv"


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


def check_if_csv_output_exists():
    if Path(csv_file_path).exists() and Path(csv_file_path).is_file():
        return True

    print(f"File: '{csv_file_name}' at path: '{csv_file_path}' does not exist ❌. Create it before proceeding...")
    return False


def format_raw_csv_entry(formatted_csv_entry, count):
    print(f"=====================================")
    print(f"Entry #{count + 1} ({formatted_csv_entry[1]}):")
    print(f"Date: {formatted_csv_entry[0]}\n"
          f"Title: {formatted_csv_entry[1]}\n"
          f"Url: {formatted_csv_entry[2]}\n"
          f"Explanation: {formatted_csv_entry[3]}\n"
          f"Logged_At: {formatted_csv_entry[4]}")


def get_line_count(count):
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

    return count