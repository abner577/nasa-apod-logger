from pathlib import Path
import json
from data_storage import DIR_PATH
from src.utils.data_utils import *

json_file_path = f"{DIR_PATH}/data/output.jsonl"


def check_if_json_output_exists():
    if Path(json_file_path).exists() and Path(json_file_path).is_file():
        print(f"{json_file_path} exists ✅")
        return True

    return False


def create_json_output_file():
    if check_if_json_output_exists():
        print(f"Cannot create file at {json_file_path} because it already exists ❌")
        return

    Path(f"{json_file_path}").touch()
    print(f"output.jsonl file created at {json_file_path} ✅")

# Wrong right now, this isnt executing not sure why
def check_for_duplicate_json_entries(formatted_apod_data):
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                print(f"Cur Line: {line}")
                if content['date'] == formatted_apod_data['date']:
                    return True

    except PermissionError:
        print(f"Dont have permission to read from {json_file_path}.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from the file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)

    return False

def log_data_to_json(formatted_apod_data):
    if not check_if_json_output_exists():
        print(f"json file {json_file_path} does not exist ❌. Create it before proceeding.")
        return

    flag = check_for_duplicate_json_entries(formatted_apod_data)
    print(f"Flag value: {flag}")
    if flag:
        print("This entry has already been logged. Not logging again.")
        return

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Dont have permission to write to {json_file_path}.")
    except Exception as e:
        print(e)


def clear_json_output_file():
    pass


def delete_json_output_file():
    pass


log_data_to_json(FORMATTED_TEST_DATA)