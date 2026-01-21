import json
from pathlib import Path
from src.config import user_settings_path, user_settings_name

default_settings = {
    "automatically_redirect": "yes"
}


def check_if_user_settings_exist():
    return Path(user_settings_path).is_file()


def create_user_settings():
    if check_if_user_settings_exist():
        print(f"File '{user_settings_name}' already exists, skipping creation.")
        return

    Path(user_settings_path).touch()

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(default_settings, ensure_ascii=False) + "\n")
    except PermissionError:
        print(f"Dont have permission to write to file: '{user_settings_name}' at path: '{user_settings_path}'.")
    except Exception as e:
        print(e)

    print(f"File '{user_settings_name}' created ✅.")


def update_user_settings():
    if not check_if_user_settings_exist():
        print(f"File '{user_settings_name}' does not exist. Create it before proceeding.")
        return

    try:
        updated_setting = input('Type "yes" to open APOD links automatically, or "no" to disable: ').strip().lower()

        if updated_setting != "yes" and updated_setting != "no":
            print('Please enter "yes" or "no".')
            return

    except Exception as e:
        print(e)
        return

    updated_settings = {"automatically_redirect": updated_setting}

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(updated_settings, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Dont have permission to write to file: '{user_settings_name}' at path: '{user_settings_path}'.")
    except Exception as e:
        print(e)

    print(f"Successfully updated '{user_settings_name}' ✅.")


def get_user_settings():
    if not check_if_user_settings_exist():
        print(f"File '{user_settings_name}' does not exist. Create it before proceeding.")
        return False

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                content = json.loads(line)
                return content.get("automatically_redirect") == "yes"

    except PermissionError:
        print(f"Dont have permission to read from file: '{user_settings_name}' ❌.")
    except Exception as e:
        print(e)

    return False

