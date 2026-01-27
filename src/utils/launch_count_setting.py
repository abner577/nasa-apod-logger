import json
from pathlib import Path
from src.config import user_settings_path, user_settings_name
from user_settings import get_user_settings

# when we update this we need to write back automatically_redirect as well which is why we call the get_user_settings method
def increment_launch_count(current_launch_count):
    current_launch_count += 1

    automatically_redirect = get_user_settings() # returns user settings

    current_launch_count_dict = {
        "launch_count": f"{current_launch_count}"
    }

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(automatically_redirect, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_launch_count_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Dont have permission to write to file: '{user_settings_name}' at path: '{user_settings_path}'.")
    except Exception as e:
        print(e)


def get_launch_count():
    pass