from pathlib import Path
from utils.data_utils import FORMATTED_TEST_DATA, FORMATTED_TEST_DATA2


DIR_PATH = "C://Users/joser/PycharmProjects/NASA-APOD-Logger"


def check_if_data_exists():
    if Path(f"{DIR_PATH}/data").is_dir():
        return True
    else:
        return False


def create_data_directory():
    if check_if_data_exists():
        print("Directory 'data' already exists ❌")
        return

    Path(f"{DIR_PATH}/data").mkdir(parents=True, exist_ok=True)
    print("Directory 'data' created ✅")



