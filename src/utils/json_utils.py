"""
json_utils.py

Helper functions for working with the JSONL APOD log.
Includes file checks, duplicate detection, and display formatting.
"""

import json

from pathlib import Path
from src.config import json_file_path, json_file_name


def create_json_output_file():
    """
     Create the JSONL output file if it does not already exist.

     Returns:
      None:
    """

    if check_if_json_output_exists():
        print(f"JSONL log already exists: '{json_file_name}'. Skipping creation.")
        return

    Path(json_file_path).touch()
    print(f"Created log file: '{json_file_name}' ✓")


def clear_json_output_file():
    """
       Clear (truncate) the JSONL output file contents.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return False

    try:
        with open(file=json_file_path, mode='w') as json_file:
            return True

    except PermissionError:
        print(f"Permission error: Unable to write '{json_file_name}' at '{json_file_path}' X")
    except Exception as e:
        print(e)

    return False

def delete_json_output_file():
    """
        Delete the JSONL output file from disk.

        Returns:
         None:
    """

    Path(f"{json_file_path}").unlink()
    print(f"Deleted: '{json_file_name}' ✓")


def get_line_count(count):
    """
      Count the number of lines in the JSONL log file.

      Args:
      count: Initial count value (typically 0).

      Returns:
       int: Total number of lines in the file.
    """

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                count += 1

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X.")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)

    return count


def check_for_duplicate_json_entries(formatted_apod_data):
    """
      Check whether a JSONL entry with the same APOD date already exists.

      Args:
      formatted_apod_data: A dict containing the APOD snapshot to compare.

      Returns:
       bool: True if a duplicate date is found, otherwise False.
    """

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                if content['date'] == formatted_apod_data['date']:
                    print(f"Skipped (duplicate): {content['date']} already exists in {json_file_name}.")
                    return True

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X.")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)

    return False


def check_if_json_output_exists():
    """
       Check whether the JSONL output file exists on disk.

       Returns:
        bool: True if the file exists, otherwise False.
    """

    if Path(json_file_path).exists() and Path(json_file_path).is_file():
        return True

    return False


def format_raw_jsonl_entry(formatted_jsonl_entry, count):
    """
       Print a single JSONL entry in a readable, numbered format.

       Args:
       formatted_jsonl_entry: A dict representing one JSONL snapshot entry.
       count: Zero-based index used for display numbering.

       Returns:
        None:
    """

    print("=====================================")
    if count == 0:
        print()
    print(
        f"Entry #{count + 1} ({formatted_jsonl_entry['title']}):\n"
        f"Date: {formatted_jsonl_entry['date']}\n"
        f"Title: {formatted_jsonl_entry['title']}\n"
        f"URL: {formatted_jsonl_entry['url']}\n"
        f"Explanation: {formatted_jsonl_entry['explanation']}\n"
        f"Logged at: {formatted_jsonl_entry['logged_at']}\n"
    )