"""
json_storage.py

JSONL persistence layer for APOD snapshots.
Responsible for creating, writing, reading, and rewriting the JSONL log.
"""
from itertools import count

from src.utils.json_utils import *
from src.utils.data_utils import *
from src.utils.date_utils import check_valid_nasa_date
from src.config import *


def create_json_output_file():
    """
     Create the JSONL output file if it does not already exist.

     Returns:
      None:
    """

    if check_if_json_output_exists():
        print(f"Cannot create file at '{json_file_path}' because it already exists ❌")
        return

    Path(f"{json_file_path}").touch()
    print(f"output.jsonl file created at '{json_file_path}' ✅")


def log_data_to_json(formatted_apod_data):
    """
       Append a formatted APOD snapshot to the JSONL log.

       Args:
       formatted_apod_data: A dict containing the snapshot fields to write.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return

    if check_for_duplicate_json_entries(formatted_apod_data):
        return

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            # One JSON object per line so we can safely append.
            # Need to use .dumps to write JSON as a string
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")
            print(f"Successfully logged data to '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def clear_json_output_file():
    """
       Clear (truncate) the JSONL output file contents.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return

    try:
        with open(file=json_file_path, mode='w') as json_file:
            print(f"Successfully cleared file: '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def delete_json_output_file():
    """
        Delete the JSONL output file from disk.

        Returns:
         None:
    """

    Path(f"{json_file_path}").unlink()
    print(f"File: {json_file_name} at path: '{json_file_path}' deleted ✅.")


def show_first_n_json_log_entries(entries_amount):
    """
        Display the first N logged JSONL entries.

        Args:
        entries_amount: Number of entries to display.

        Returns:
         None:
    """

    if entries_amount < 1:
        print("Amount of entries cannot be less than 1.")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(0)

    if entries_amount > line_count:
        print(f"We only have {line_count} entries in total. Displaying all the entries that we have...")
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
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)


def show_last_n_json_log_entries(entries_amount):
    """
    Display the last N logged JSONL entries.

       Args:
    entries_amount: Number of entries to display.

       Returns:
        None:
    """

    entries_list = []

    if entries_amount < 1:
        print("Amount of entries cannot be less than 1.")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(count=0)

    if entries_amount > line_count:
        print(f"We only have {line_count} entries in total. Displaying all the entries that we have...")
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
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
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
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)


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

    year = int(input("Enter a year (YYYY): "))
    month = int(input("Enter a month (MM): "))
    day = int(input("Enter a day (DD): "))

    date_object = datetime.date(year, month, day)

    check_result = check_valid_nasa_date(date_object)

    if check_result is not None:
        print(check_result)
        return

    found = False
    target_date = date_object.isoformat()

    try:
        # Read phase
        # Need to rewrite the entire file: you can't delete a single JSONL line in-place safely.
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] == target_date:
                    print(f"This entry has been found ✅.")
                    found = True

                else:
                    entries_to_keep.append(content)

            if not found:
                print(f"This entry was not found ❌.")
                return

            else:
                print("Removing entry...")
            # Write phase
            with open(file=json_file_path, mode='w') as file:
                for entry in entries_to_keep:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
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
                print(f"{json_file_name} is empty ❌.")
                return

            most_recent_apod = format_apod_data(most_recent_apod)
            format_raw_jsonl_entry(most_recent_apod, 0)

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
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
                print(f"{json_file_name} is empty ❌.")
                return

            most_recent_apod = format_apod_data(oldest_apod)
            format_raw_jsonl_entry(oldest_apod, 0)

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)


def log_multiple_json_entries():
    """
       Log multiple APOD entries to jsonl.

       Returns:
           None:
    """

    pass

