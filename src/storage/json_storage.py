from pathlib import Path
import json
from data_storage import DIR_PATH
from src.utils.data_utils import *

json_file_path = f"{DIR_PATH}/data/output.jsonl"
json_file_name = "output.jsonl"


def check_if_json_output_exists():
    if Path(json_file_path).exists() and Path(json_file_path).is_file():
        print(f"File: '{json_file_name}' at path: '{json_file_path}' found ✅.")
        return True

    print(f"File: '{json_file_name}' at path: '{json_file_path}' not found ❌.")
    return False


def create_json_output_file():
    if check_if_json_output_exists():
        print(f"Cannot create file at '{json_file_path}' because it already exists ❌")
        return

    Path(f"{json_file_path}").touch()
    print(f"output.jsonl file created at '{json_file_path}' ✅")


def check_for_duplicate_json_entries(formatted_apod_data):
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                if content['date'] == formatted_apod_data['date']:
                    print(f"APOD with date: '{content['date']}' found in: '{json_file_name}'. Not logging again ⛔")
                    return True

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)

    return False


def log_data_to_json(formatted_apod_data):
    if not check_if_json_output_exists():
        return

    if check_for_duplicate_json_entries(formatted_apod_data):
        return

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")
            print(f"Successfully logged data to '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def clear_json_output_file():
    try:
        with open(file=json_file_path, mode='w') as json_file:
            print(f"Successfully cleared file: '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def delete_json_output_file():
    Path(f"{json_file_path}").unlink()
    print(f"File: {json_file_name} at path: '{json_file_path}' deleted ✅.")


def show_first_n_json_log_entries(entries_amount):
    if entries_amount < 1:
        print("Amount of entries cannot be less than 1.")
        return

    count = 0

    if not check_if_json_output_exists():
        return

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                count += 1

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)

    if entries_amount > count:
        print(f"We only have {count} entries in total. Displaying all the entries that we have...")
        entries_amount = count
    count = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

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


def format_raw_jsonl_entry(formatted_jsonl_entry, count):
    print(f"=====================================")
    print(f"Entry #{count + 1} ({formatted_jsonl_entry['title']}):")
    print(f"Date: {formatted_jsonl_entry['date']}\n"
          f"Title: {formatted_jsonl_entry['title']}\n"
          f"Url: {formatted_jsonl_entry['url']}\n"
          f"Explanation: {formatted_jsonl_entry['explanation']}\n"
          f"Logged_At: {formatted_jsonl_entry['logged_at']}")


def fetch_most_recent_json_apod():
    pass


def fetch_oldest_json_apod():
    pass


def show_all_json_entries():
    pass

def get_line_count(count):
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                count += 1

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)

    return count


def show_last_n_json_log_entries(entries_amount):
    entries_list = []

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
    removed_counter = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                content = json.loads(line)
                entries_list.append(content)
                count += 1

                if count > entries_amount:
                    entries_list.remove(entries_list[removed_counter])
                    removed_counter += 1


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


