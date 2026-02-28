from typing import Any
import json
from pathlib import Path

from rich.text import Text

from src.config import user_settings_name, user_settings_path
from src.startup.console import console
from src.utils.box_utils import build_box_lines, stylize_line


initial_automatically_redirect_dict = {
    "automatically_redirect": "yes"
}

initial_launch_count_dict = {
    "launch_count": "0"
}

initial_automatically_set_wallpaper_dict = {
    "automatically_set_wallpaper": "no"
}

initial_automatically_save_apod_files_dict = {
    "automatically_save_apod_files": "no"
}


def _normalize_and_persist_settings(settings_dict: dict) -> dict:
    normalized_settings = {
        "automatically_redirect": settings_dict.get("automatically_redirect", "yes"),
        "launch_count": settings_dict.get("launch_count", "0"),
        "automatically_set_wallpaper": settings_dict.get("automatically_set_wallpaper", "no"),
        "automatically_save_apod_files": settings_dict.get("automatically_save_apod_files", "no"),
    }

    with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
        file.write(json.dumps({"automatically_redirect": normalized_settings["automatically_redirect"]}, ensure_ascii=False) + "\n")
        file.write(json.dumps({"launch_count": normalized_settings["launch_count"]}, ensure_ascii=False) + "\n")
        file.write(json.dumps({"automatically_set_wallpaper": normalized_settings["automatically_set_wallpaper"]}, ensure_ascii=False) + "\n")
        file.write(json.dumps({"automatically_save_apod_files": normalized_settings["automatically_save_apod_files"]}, ensure_ascii=False) + "\n")

    return normalized_settings


def check_if_user_settings_exist() -> Any:
    return Path(user_settings_path).is_file()


def create_user_settings() -> Any:
    if check_if_user_settings_exist():
        print(f"Settings file already exists: '{user_settings_name}'. Skipping creation.")
        return

    Path(user_settings_path).touch()

    try:
        with open(file=user_settings_path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(initial_automatically_redirect_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(initial_launch_count_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(initial_automatically_set_wallpaper_dict, ensure_ascii=False) + "\n")
            file.write(json.dumps(initial_automatically_save_apod_files_dict, ensure_ascii=False) + "\n")

    except PermissionError:
        print(f"Permission error: Unable to write '{user_settings_name}' at '{user_settings_path}' X")
    except Exception as e:
        print(e)

    print(f"Created settings file: '{user_settings_name}' ✓")


def get_all_user_settings() -> Any:
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

        return _normalize_and_persist_settings(settings_dict)

    except PermissionError:
        print(f"Permission error: Unable to read '{user_settings_name}' at '{user_settings_path}' X")
    except Exception as e:
        print(e)

    return None


def _prompt_yes_no(prompt_text: str) -> str | None:
    try:
        prompt = Text(f"\n{prompt_text} ", style="app.secondary")
        prompt.append("(y/n): ", style="app.primary")
        console.print(prompt, end="")

        updated_setting = input().strip().lower()
        if updated_setting in ("y", "yes"):
            return "yes"
        if updated_setting in ("n", "no"):
            return "no"

        msg = Text("\nInput error: ", style="err")
        msg.append('Please enter "y" or "n".\n', style="body.text")
        console.print(msg)
        return None

    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))
        return None


def update_automatically_redirect_setting() -> Any:
    if not check_if_user_settings_exist():
        msg = Text("Settings file not found: ", style="err")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(". Please create it first.", style="body.text")
        console.print(msg)
        return

    updated_setting = _prompt_yes_no("Auto-open APOD links in your browser?")
    if updated_setting is None:
        return

    settings_dict = get_all_user_settings()
    if not settings_dict:
        return

    settings_dict["automatically_redirect"] = updated_setting

    try:
        _normalize_and_persist_settings(settings_dict)
    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{user_settings_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)
        return
    except Exception as e:
        console.print(Text(str(e), style="err"))
        return

    console.print()
    msg = Text("Updated ", style="body.text")
    msg.append("'auto-redirect' ", style="app.primary")
    msg.append("setting", style="body.text")
    msg.append(" ✓", style="ok")
    console.print(msg)
    console.print()


def get_automatically_redirect_setting() -> Any:
    settings_dict = get_all_user_settings()
    if settings_dict is None:
        return None
    return {"automatically_redirect": settings_dict.get("automatically_redirect", "yes")}


def increment_launch_count(current_launch_count: Any) -> Any:
    current_launch_count += 1

    settings_dict = get_all_user_settings()
    if not settings_dict:
        return

    settings_dict["launch_count"] = f"{current_launch_count}"

    try:
        _normalize_and_persist_settings(settings_dict)
    except PermissionError:
        print(f"Permission error: Unable to write '{user_settings_name}' at '{user_settings_path}' X")
    except Exception as e:
        print(e)


def get_launch_count() -> Any:
    settings_dict = get_all_user_settings()
    if settings_dict is None:
        return None
    return {"launch_count": settings_dict.get("launch_count", "0")}


def get_automatically_set_wallpaper() -> Any:
    settings_dict = get_all_user_settings()
    if settings_dict is None:
        return None
    return {"automatically_set_wallpaper": settings_dict.get("automatically_set_wallpaper", "no")}


def get_automatically_save_apod_files() -> Any:
    settings_dict = get_all_user_settings()
    if settings_dict is None:
        return None
    return {"automatically_save_apod_files": settings_dict.get("automatically_save_apod_files", "no")}


def update_automatically_set_wallpaper() -> Any:
    if not check_if_user_settings_exist():
        msg = Text("Settings file not found: ", style="err")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(". Please create it first.", style="body.text")
        console.print(msg)
        return

    updated_setting = _prompt_yes_no("Automatically set APOD as wallpaper?")
    if updated_setting is None:
        return

    settings_dict = get_all_user_settings()
    if not settings_dict:
        return

    settings_dict["automatically_set_wallpaper"] = updated_setting

    try:
        _normalize_and_persist_settings(settings_dict)
    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{user_settings_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)
        return
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))
        return

    console.print()
    msg = Text("Updated ", style="body.text")
    msg.append("'auto-set-wallpaper' ", style="app.primary")
    msg.append("setting", style="body.text")
    msg.append(" ✓", style="ok")
    console.print(msg)
    console.print()


def update_automatically_save_apod_files_setting() -> Any:
    if not check_if_user_settings_exist():
        msg = Text("Settings file not found: ", style="err")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(". Please create it first.", style="body.text")
        console.print(msg)
        return

    updated_setting = _prompt_yes_no("Automatically save APOD media files?")
    if updated_setting is None:
        return

    settings_dict = get_all_user_settings()
    if not settings_dict:
        return

    settings_dict["automatically_save_apod_files"] = updated_setting

    try:
        _normalize_and_persist_settings(settings_dict)
    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{user_settings_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{user_settings_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)
        return
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))
        return

    console.print()
    msg = Text("Updated ", style="body.text")
    msg.append("'auto-save-apod-files' ", style="app.primary")
    msg.append("setting", style="body.text")
    msg.append(" ✓", style="ok")
    console.print(msg)
    console.print()


def stylize_settings_content(t: Text) -> None:
    s = t.plain
    if not s or not s.startswith("│"):
        return

    def is_boundary(ch: str) -> bool:
        return ch == "" or (not ch.isalnum())

    def stylize_substring(substr: str, style: str) -> None:
        i = s.find(substr)
        if i != -1:
            t.stylize(style, i, i + len(substr))

    stylize_substring("Auto-open in browser:", "app.secondary")
    stylize_substring("Auto-set-wallpaper:", "app.secondary")
    stylize_substring("Auto-save APOD files:", "app.secondary")
    stylize_substring("Amount of times logged in:", "app.secondary")

    start = 0
    while True:
        i = s.find("ON", start)
        if i == -1:
            break
        left = s[i - 1] if i - 1 >= 0 else ""
        right = s[i + 2] if i + 2 < len(s) else ""
        if is_boundary(left) and is_boundary(right):
            t.stylize("ok", i, i + 2)
        start = i + 2

    start = 0
    while True:
        i = s.find("OFF", start)
        if i == -1:
            break
        left = s[i - 1] if i - 1 >= 0 else ""
        right = s[i + 3] if i + 3 < len(s) else ""
        if is_boundary(left) and is_boundary(right):
            t.stylize("err", i, i + 3)
        start = i + 3

    marker = "Amount of times logged in:"
    i = s.find(marker)
    if i != -1:
        j = i + len(marker)
        while j < len(s) and s[j] == " ":
            j += 1
        k = j
        while k < len(s) and s[k].isdigit():
            k += 1
        if k > j:
            t.stylize("app.primary", j, k)


def print_settings_box(settings_dict: dict) -> None:
    auto_redirect = settings_dict.get("automatically_redirect", "no")
    auto_wallpaper = settings_dict.get("automatically_set_wallpaper", "no")
    auto_save_apod_files = settings_dict.get("automatically_save_apod_files", "no")
    launch_count = settings_dict.get("launch_count", "0")

    lines = [
        f"Auto-open in browser:       {'✓ ON' if auto_redirect == 'yes' else 'X OFF'}",
        f"Auto-set-wallpaper:         {'✓ ON' if auto_wallpaper == 'yes' else 'X OFF'}",
        f"Auto-save APOD files:       {'✓ ON' if auto_save_apod_files == 'yes' else 'X OFF'}",
        f"Amount of times logged in:  {launch_count}",
    ]

    box_lines = build_box_lines("SETTINGS:", lines, padding_x=2)

    for raw in box_lines:
        t = Text(raw, style="body.text")
        stylize_line(t)
        stylize_settings_content(t)
        console.print(t)
