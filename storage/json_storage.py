from pathlib import Path
import json
from data_storage import DIR_PATH
from utils.data_utils import FORMATTED_TEST_DATA, FORMATTED_TEST_DATA2

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


def log_data_to_json(formatted_apod_data):
    if not check_if_json_output_exists():
        print(f"json file {json_file_path} does not exist ❌. Create it before proceeding.")
        return

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            json.dump(formatted_apod_data, json_file, ensure_ascii=False, indent=0)

    except PermissionError:
        print(f"Dont have permission to write to {json_file_path}.")
    except Exception as e:
        print(e)

