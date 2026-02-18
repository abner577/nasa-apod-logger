"""
json_storage.py

JSONL persistence layer for APOD snapshots.
Responsible for creating, writing, reading, and rewriting the JSONL log.
"""

from src.utils.json_utils import *
from src.utils.data_utils import *
from src.nasa.nasa_date import check_valid_nasa_date
from src.config import json_file_path, json_file_name, NASA_APOD_START_DATE, DATE_TODAY


def log_data_to_json(formatted_apod_data):
    """
       Append a formatted APOD snapshot to the JSONL log.

       Args:
       formatted_apod_data: A dict containing the snapshot fields to write.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return None

    if check_for_duplicate_json_entries(formatted_apod_data):
        return "Duplicate found."

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            # One JSON object per line so we can safely append.
            # Need to use .dumps to write JSON as a string
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")
            print(f"Saved: APOD '{formatted_apod_data['date']}' -> {json_file_name} ✓")

    except PermissionError:
        print(f"Permission error: Unable to write '{json_file_name}' at '{json_file_path}' X")
    except Exception as e:
        print(e)

    return None


def show_first_n_json_log_entries():
    """
        Display the first N logged JSONL entries.

        Args:
        entries_amount: Number of entries to display.

        Returns:
         None:
    """

    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        print("Invalid input. Enter a valid number.\n")
        return
    except Exception as e:
        print(e)
        return

    if entries_amount < 1:
        print("Invalid input. Enter a number of 1 or more.\n")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(0)

    if line_count == 0:
        print("\nNo entries found.\n")
        return

    if entries_amount > line_count:
        print(f"Only {line_count} entries available. Showing all.\n")
        entries_amount = line_count
    count = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                # Need to use .loads to convert JSON string --> dict
                # Since we used .dumps we need to use .loads to read the proper format
                content = json.loads(line)
                format_raw_jsonl_entry(content, count)
                count += 1
                if count == entries_amount:
                    break

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)


def show_last_n_json_log_entries():
    """
    Display the last N logged JSONL entries.

       Args:
    entries_amount: Number of entries to display.

       Returns:
        None:
    """

    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        print("Invalid input: Enter a valid number.\n")
        return
    except Exception as e:
        print(e)
        return

    entries_list = []

    if entries_amount < 1:
        print("Invalid input. Enter a number of 1 or more.\n")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(count=0)

    if line_count == 0:
        print("\nNo entries found.\n")
        return

    if entries_amount > line_count:
        print(f"Only {line_count} entries available. Showing all.\n")
        entries_amount = line_count

    count = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                entries_list.append(content)
                count += 1

                if count > entries_amount:
                    entries_list.remove(entries_list[0])
                    count -= 1

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)

    count = 0
    for entry in entries_list:
        format_raw_jsonl_entry(entry, count)
        count += 1


def show_all_json_entries():
    """
        Display all logged JSONL entries.

    Returns:
        None:
    """

    if not check_if_json_output_exists():
        return

    count = 0
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                format_raw_jsonl_entry(content, count)
                count += 1

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)

    if count == 0:
        print("\nNo entries found.\n")
        return


def delete_one_json_entry():
    """
       Delete a single JSONL entry by its APOD date.

       Prompts the user for a date, removes the matching JSON object, and rewrites
       the JSONL file with the remaining entries.

       Returns:
        None:
    """

    entries_to_keep = []

    if not check_if_json_output_exists():
        pass

    try:
        year = int(input("\nYear (YYYY): "))
        month = int(input("Month (MM): "))
        day = int(input("Day (DD): "))

    except ValueError:
        print("Invalid input. Year, month, and day must be numbers.\n")
        return
    except Exception as e:
        print(e)
        return

    date_object = datetime.date(year, month, day)
    check_result = check_valid_nasa_date(date_object)

    if check_result is not None:
        print(check_result)
        return

    target_date = date_object.isoformat()
    found = False

    try:
        # Read phase
        # Need to rewrite the entire file: you can't delete a single JSONL line in-place safely.
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] == target_date:
                    found = True

                else:
                    entries_to_keep.append(content)

            if not found:
                print(f"\nNo entry found for {target_date} X\n")
                return

            else:
                print(f"\nDeleted entry: {target_date} ✓\n")
            # Write phase
            with open(file=json_file_path, mode='w') as file:
                for entry in entries_to_keep:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission error: Unable to read/write '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)


def fetch_most_recent_json_apod():
    """
         Fetch the most recent APOD (by date) from the jsonl log.
         Doesn't matter in which order it was logged.
         Ex: Todays APOD will always be the most recent.

         Returns:
             None:
    """
    if not check_if_json_output_exists():
        return

    most_recent_date = NASA_APOD_START_DATE.isoformat()
    most_recent_apod = None

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] >= most_recent_date:
                    most_recent_date = content['date']
                    most_recent_apod = content

            if most_recent_apod is None:
                print(f"\nNo entries found in {json_file_name}.\n")
                return

            most_recent_apod = format_apod_data(most_recent_apod)
            print()
            format_raw_jsonl_entry(most_recent_apod, 0)

    except PermissionError:
        print(f"Permission error: Unable to read '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)


def fetch_oldest_json_apod():
    """
        Fetch the oldest APOD (by date) from the CSV log.
        Doesn't matter in which order it was logged.
        Ex: First APOD ever uploaded will always be the oldest.

        Returns:
            None:
    """

    if not check_if_json_output_exists():
        return

    oldest_date = DATE_TODAY.isoformat()
    oldest_apod = None

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] <= oldest_date:
                    oldest_date = content['date']
                    oldest_apod = content

            if oldest_apod is None:
                print(f"{json_file_name} is empty.")
                return

            oldest_apod = format_apod_data(oldest_apod)
            print()
            format_raw_jsonl_entry(oldest_apod, 0)

    except PermissionError:
        print(f"Permission error: Unable to write '{json_file_name}' at '{json_file_path}' X")
    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
    except Exception as e:
        print(e)


def log_multiple_json_entries(list_formatted_apod_data):
    """
       Log multiple APOD entries to jsonl.

       Returns:
           None:
    """
    for entry in list_formatted_apod_data:
        log_data_to_json(entry)