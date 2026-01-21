import json
from pathlib import Path
from src.config import user_settings_path, user_settings_name

default_settings = {
    'automatically_redirect': 'yes'
}


def check_if_user_settings_exist():
    if Path(user_settings_path).is_file():
        return True

    return False


def create_user_settings():
    if check_if_user_settings_exist():
        print(f"File '{user_settings_name}' already exists, skipping creation.")
        return

    Path(user_settings_path).touch()

    try:
        with open(file=user_settings_path, mode='w', encoding='utf-8') as file:
            file.write(json.dumps(default_settings, ensure_ascii=False) + "\n")
    except PermissionError:
        print(f"Dont have permission to write to file: '{user_settings_name}' at path: '{user_settings_path}'.")
    except Exception as e:
        print(e)

    print(f"File '{user_settings_name}' created ✅.")


# Write to file with something like:
# automatically_redirect: yes/no
def update_user_settings():
    if not check_if_user_settings_exist():
        print(f"File '{user_settings_name}' does not exist. Create it before proceeding.")
        return

    try:
        updated_setting = input(("Enter 'yes' to enable automatic redirect OR "
                                 "Enter 'no' to disable automatic redirect\n"))

    except ValueError:
        print("Please enter 'yes' or 'no'")
        return
    except Exception as e:
        print(e)
        return

    updated_settings = {'automatically_redirect': updated_setting}

    try:
        with open(file=user_settings_path, mode="w", encoding='utf-8') as file:
            file.write(json.dumps(updated_settings, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Dont have permission to write to file: '{user_settings_name}' at path: '{user_settings_path}'.")
    except Exception as e:
        print(e)

    print(f"Successfully updated '{user_settings_name}' ✅.")


def get_user_settings():
    if not check_if_user_settings_exist():
        print(f"File '{user_settings_name}' does not exist. Create it before proceeding.")
        return

    try:
        with open(file=user_settings_path, mode='r', encoding='utf-8') as file:
            for line in file:
                content = json.loads(line)
                if content['automatically_redirect'] == 'yes':
                    print("You will be automatically directed to url's ✅.")
                else:
                    print("You wont be automatically directed to url's ❌.")

    except PermissionError:
        print(f"Dont have permission to read from file: '{user_settings_name}' ❌.")
    except Exception as e:
        print(e)
