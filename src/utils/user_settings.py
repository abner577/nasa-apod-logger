import json
from pathlib import Path
from src.config import user_settings_path, user_settings_name

initial_automatically_redirect_dict = {
    "automatically_redirect": "yes"
}

initial_launch_count_dict = {
    "launch_count": "0"
}

initial_automatically_set_wallpaper_dict = {
    "automatically_set_wallpaper": "no"
}


def check_if_user_settings_exist():
    return Path(user_settings_path).is_file()


def create_user_settings():
    if check_if_user_settings_exist():
        print(f"Settings file already exists: '{user_settings_name}'. Skipping.")
        return

    Path(user_settings_path).touch()

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(initial_automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(initial_launch_count_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(initial_automatically_set_wallpaper_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission denied: Unable to write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    print(f"Created settings file: '{user_settings_name}' ✅")


def get_all_user_settings():
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return None

    settings_dict = {}

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                if not line:
                    continue

                content = json.loads(line)
                settings_dict.update(content)

            return settings_dict

    except PermissionError:
        print(f"Permission denied: Unable to read '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    return None


def format_all_user_settings(settings_dict):
   if settings_dict['automatically_redirect'] == 'yes':
    print(f"Auto-open in browser: ON ✅")
   else:
    print(f"Auto-open in browser: OFF ❌")

   if settings_dict['automatically_set_wallpaper'] == 'yes':
    print(f"Auto-set-wallpaper: ON ✅")
   else:
    print(f"Auto-set-wallpaper: OFF ❌")

   print(f"Amount of times logged in: {settings_dict['launch_count']}")


# when we update, we need to write back all the other settings as well
def update_automatically_redirect_setting():
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return

    try:
        updated_setting = input('\nAuto-open APOD links in your browser? (y/n): ').strip().lower()

        if updated_setting == "y" or updated_setting == "yes":
            updated_setting = "yes"
        elif updated_setting == "n" or updated_setting == "no":
            updated_setting = "no"
        else:
            print('Invalid input. Please enter "y" or "n".\n')
            return

    except Exception as e:
        print(e)
        return

    current_automatically_redirect_dict = {"automatically_redirect": updated_setting}
    current_launch_count_dict = get_launch_count()
    current_wallpaper_dict = get_automatically_set_wallpaper()

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(current_automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_launch_count_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_wallpaper_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission denied: Unable to read/write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    print(f"Updated settings: '{user_settings_name}' ✅")


def get_automatically_redirect_setting():
    """
    Returns line 1 dict: {"automatically_redirect": "..."}
    """
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return None

    count = 0

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                count += 1
                content = json.loads(line)

                if count == 1:
                    return content

    except PermissionError:
        print(f"Permission denied: Unable to write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    return None


def increment_launch_count(current_launch_count):
    """
     Updates launch_count (line 2) and writes back automatically_redirect (line 1)
     AND automatically_set_wallpaper (line 3).
     """
    current_launch_count += 1

    current_automatically_redirect_dict = get_automatically_redirect_setting() # returns user settings
    current_wallpaper_dict = get_automatically_set_wallpaper()

    current_launch_count_dict = {
        "launch_count": f"{current_launch_count}"
    }

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(current_automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_launch_count_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_wallpaper_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission denied: Unable to write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)


def get_launch_count():
    """
    Returns line 2 dict: {"launch_count": "..."}
    """
    count = 0

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                count += 1
                content = json.loads(line)
                if count == 2:
                    return content

    except PermissionError:
        print(f"Permission denied: Unable to read '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

def get_automatically_set_wallpaper():
    """
       Returns line 3 dict: {"automatically_set_wallpaper": "..."}
    """
    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return None

    count = 0

    try:
        with open(file=user_settings_path, mode="r", encoding="utf-8") as file:
            for line in file:
                if not line:
                    continue
                count += 1
                content = json.loads(line)
                if count == 3:
                    return content

    except PermissionError:
        print(f"Permission denied: Unable to read '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    # If we got here, line 3 doesn't exist yet
    return initial_automatically_set_wallpaper_dict

def update_automatically_set_wallpaper():
    """
    Updates automatically_set_wallpaper (line 3) and writes back:
    - automatically_redirect (line 1)
    - launch_count (line 2)
    """

    if not check_if_user_settings_exist():
        print(f"Settings file not found: '{user_settings_name}'. Please create it first.")
        return

    try:
        updated_setting = input('\nAutomatically set APOD as wallpaper? (y/n): ').strip().lower()

        if updated_setting == "y" or updated_setting == "yes":
            updated_setting = "yes"
        elif updated_setting == "n" or updated_setting == "no":
            updated_setting = "no"
        else:
            print('Invalid input. Please enter "y" or "n".\n')
            return

    except Exception as e:
        print(e)
        return

    current_automatically_redirect_dict = get_automatically_redirect_setting()
    current_launch_count_dict = get_launch_count()
    current_wallpaper_dict = {"automatically_set_wallpaper": updated_setting}

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(current_automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_launch_count_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(current_wallpaper_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission denied: Unable to read/write '{user_settings_name}' at '{user_settings_path}' ❌")
    except Exception as e:
        print(e)

    print(f"Updated settings: '{user_settings_name}' ✅")