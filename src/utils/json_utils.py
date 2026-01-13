import json

from src.storage.data_storage import DIR_PATH
from pathlib import Path

json_file_path = f"{DIR_PATH}/data/output.jsonl"
json_file_name = "output.jsonl"

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


def check_if_json_output_exists():
    if Path(json_file_path).exists() and Path(json_file_path).is_file():
        print(f"File: '{json_file_name}' at path: '{json_file_path}' found ✅.")
        return True

    print(f"File: '{json_file_name}' at path: '{json_file_path}' not found ❌.")
    return False