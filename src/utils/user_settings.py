import json
from pathlib import Path
from src.config import user_settings_path, user_settings_name

automatically_redirect_dict = {
    "automatically_redirect": "yes"
}

launch_count_dict = {
    "launch_count": "0"
}


def check_if_user_settings_exist():
    return Path(user_settings_path).is_file()

# Need to update this to automatically write launch_count to 0
def create_user_settings():
    if check_if_user_settings_exist():
        print(f"Settings file already exists: '{user_settings_name}'. Skipping.")
        return

    Path(user_settings_path).touch()

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(launch_count_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission denied: Unable to write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    print(f"Created settings file: '{user_settings_name}' ✅")


# when we update, we need to write back the second setting as well
# so we would call the get_line_count method
def update_user_settings():
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return

    try:
        updated_setting = input('\nAuto-open APOD links in your browser? Type "yes" or "no": ').strip().lower()

        if updated_setting != "yes" and updated_setting != "no":
            print('Invalid input. Please enter "yes" or "no".\n')
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

    print(f"Updated settings: '{user_settings_name}' ✅")


def get_user_settings():
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return None

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                content = json.loads(line)
                return content

    except PermissionError:
        print(f"Permission denied: Unable to write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    return None

create_user_settings()