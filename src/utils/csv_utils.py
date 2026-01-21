"""
csv_utils.py

Helper functions for working with the CSV APOD log.
Includes duplicate detection, file checks, and display formatting.
"""

import csv

from pathlib import Path
from src.config import DIR_PATH, csv_file_path, csv_file_name

HEADERS = {
    "date": "",
    "title": "",
    "url": "",
    "explanation": "",
    "logged_at": "",
}


def create_csv_output_file():
    """
     Create the CSV output file if it does not already exist.

     Returns:
         None:
    """

    if check_if_csv_output_exists():
        return

    Path(csv_file_path).touch()
    write_header_to_csv()
    print(f"Created: '{csv_file_name}' at '{csv_file_path}'. ✅")


def clear_csv_output_file():
    """
       Clear (truncate) the CSV output file contents.

       Returns:
           None:
    """

    try:
        with open(file=csv_file_path, mode='w', encoding='utf-8') as csv_file:
            print(f"Cleared: '{csv_file_name}'.")

    except PermissionError:
        print(f"Permission denied: Unable to write '{csv_file_name}' at '{csv_file_path}' ❌")
    except Exception as e:
        print(e)


def delete_csv_output_file():
    """
       Delete the CSV output file from disk.

       Returns:
           None:
    """

    Path(f"{csv_file_path}").unlink()
    print(f"Deleted: '{csv_file_name}' at '{csv_file_path}'.")


def write_header_to_csv():
    """
    Write the CSV header row to the output file.

    Returns:
        None:
    """

    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=HEADERS.keys())
            writer.writeheader()

    except PermissionError:
        print(f"Permission denied: Unable to write '{csv_file_name}' at '{csv_file_path}' ❌")
    except Exception as e:
        print(e)


def check_for_duplicate_csv_entries(formatted_apod_data):
    """
       Check whether a CSV entry with the same APOD date already exists.

       Args:
       formatted_apod_data: A dict containing the APOD snapshot to compare.

       Returns:
        bool: True if a duplicate date is found, otherwise False.
    """

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
        print(f"Permission denied: Unable to read '{csv_file_name}' at '{csv_file_path}' ❌")
    except Exception as e:
        print(e)

    return False


def check_if_csv_output_exists():
    """
      Check whether the CSV output file exists on disk.

      Returns:
       bool: True if the file exists, otherwise False.
    """

    if Path(csv_file_path).exists() and Path(csv_file_path).is_file():
        return True

    print(f"Missing file: '{csv_file_name}' at '{csv_file_path}'. Create it before proceeding.")
    return False


def format_raw_csv_entry(formatted_csv_entry, count):
    """
       Print a single CSV entry in a readable, numbered format.

       Args:
       formatted_csv_entry: A list representing one CSV row.
       count: Zero-based index used for display numbering.

       Returns:
        None:
    """

    print(f"=====================================")
    print(f"Entry #{count + 1} ({formatted_csv_entry[1]}):")
    print(f"Date: {formatted_csv_entry[0]}\n"
          f"Title: {formatted_csv_entry[1]}\n"
          f"Url: {formatted_csv_entry[2]}\n"
          f"Explanation: {formatted_csv_entry[3]}\n"
          f"Logged_At: {formatted_csv_entry[4]}")


def get_line_count(count):
    """
       Count the number of data rows in the CSV file.

       Args:
       count: Initial count value (typically 0).

       Returns:
        int: Total number of data rows in the file.
       """

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