"""
json_utils.py

Helper functions for working with the JSONL APOD log.
Includes file checks, duplicate detection, and display formatting.
"""

import json

from pathlib import Path
from src.config import json_file_path, json_file_name, DATA_DIR
from rich.text import Text
from src.startup.console import console


def create_json_output_file():
    """
     Create the JSONL output file if it does not already exist.

     Returns:
      None:
    """

    if check_if_json_output_exists():
        msg = Text("\nJSONL log already exists: ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Skipping creation.", style="body.text")
        console.print(msg)
        return

    Path(json_file_path).touch()
    msg = Text("Created log file: ", style="ok")
    msg.append(f"'{json_file_name}' ", style="app.primary")
    msg.append("✓", style="ok")
    console.print(msg)


def clear_json_output_file():
    """
       Clear (truncate) the JSONL output file contents.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return False

    try:
        with open(file=json_file_path, mode='w') as json_file:
            viewer_dir = DATA_DIR / "viewer"
            if viewer_dir.exists() and viewer_dir.is_dir():
                for html_file in viewer_dir.glob("*.html"):
                    html_file.unlink()
            return True

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to write ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return False

def delete_json_output_file():
    """
        Delete the JSONL output file from disk.

        Returns:
         None:
    """

    Path(f"{json_file_path}").unlink()
    msg = Text("Deleted: ", style="ok")
    msg.append(f"'{json_file_name}' ", style="app.primary")
    msg.append("✓", style="ok")
    console.print(msg)


def get_line_count(count):
    """
      Count the number of lines in the JSONL log file.

      Args:
      count: Initial count value (typically 0).

      Returns:
       int: Total number of lines in the file.
    """

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                count += 1

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X.", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        msg = Text("\nJSONL parse error: ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return count


def check_for_duplicate_json_entries(formatted_apod_data):
    """
      Check whether a JSONL entry with the same APOD date already exists.

      Args:
      formatted_apod_data: A dict containing the APOD snapshot to compare.

      Returns:
       bool: True if a duplicate date is found, otherwise False.
    """

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                if content['date'] == formatted_apod_data['date']:
                    msg = Text("Skipped (duplicate entry): ", style="app.secondary")
                    msg.append(str(content["date"]), style="app.primary")
                    msg.append(" already exists in ", style="body.text")
                    msg.append(str(json_file_name), style="app.primary")
                    msg.append(".", style="body.text")
                    console.print(msg)
                    return True

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X.", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        msg = Text("\nJSONL parse error: ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return False


def check_if_json_output_exists():
    """
       Check whether the JSONL output file exists on disk.

       Returns:
        bool: True if the file exists, otherwise False.
    """

    if Path(json_file_path).exists() and Path(json_file_path).is_file():
        return True

    return False


def format_raw_jsonl_entry(formatted_jsonl_entry, count):
    """
       Print a single JSONL entry in a readable, numbered format.

       Args:
       formatted_jsonl_entry: A dict representing one JSONL snapshot entry.
       count: Zero-based index used for display numbering.

       Returns:
        None:
    """

    console.print("─" * 60, style="app.secondary")

    entry_number = count + 1
    title = formatted_jsonl_entry["title"]
    date = formatted_jsonl_entry["date"]
    url = formatted_jsonl_entry["url"]
    explanation = formatted_jsonl_entry["explanation"]
    logged_at = formatted_jsonl_entry["logged_at"]
    local_file_path = formatted_jsonl_entry.get("local_file_path", "")
    if not local_file_path:
        local_file_path = "Not saved yet"

    header = Text(f"Entry #{entry_number} ({title}):\n", style="app.primary")
    console.print(header)

    # Date
    line = Text()
    line.append("Date: ", style="app.secondary")
    line.append(f"{date}\n", style="body.text")

    # Title
    line.append("Title: ", style="app.secondary")
    line.append(f"{title}\n", style="body.text")

    # URL
    line.append("URL: ", style="app.secondary")
    line.append(f"{url}\n", style="app.url")

    # Explanation
    line.append("Explanation: ", style="app.secondary")
    line.append(f"{explanation}\n", style="body.text")

    # Logged at
    line.append("Logged at: ", style="app.secondary")
    line.append(f"{logged_at}\n", style="body.text")

    # Local file path
    line.append("Local file path: ", style="app.secondary")
    line.append(f"{local_file_path}\n", style="app.url")

    console.print(line)
