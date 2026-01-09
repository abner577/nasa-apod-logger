from pathlib import Path
import csv
from data_storage import DIR_PATH
from utils.data_utils import FORMATTED_TEST_DATA, FORMATTED_TEST_DATA2

csv_file_path = f"{DIR_PATH}/data/output.csv"

def check_if_csv_output_exists():
    if Path(csv_file_path).exists() and Path(csv_file_path).is_file():
        print(f"{csv_file_path} exists ✅")
        return True

    return False


def create_csv_output_file():
    if check_if_csv_output_exists():
        print(f"Cannot create file at {csv_file_path} because it already exists ❌")
        return

    Path(f"{csv_file_path}").touch()
    print(f"output.csv file created at {csv_file_path} ✅")


def log_data_to_csv(formatted_apod_data):
    if not check_if_csv_output_exists():
        print(f"csv file {csv_file_path} does not exist ❌. Create it before proceeding.")
        return

    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=formatted_apod_data.keys())
            writer.writeheader()
            writer.writerow(formatted_apod_data)

    except PermissionError:
        print(f"Dont have permission to write to {csv_file_path}.")
    except Exception as e:
        print(e)