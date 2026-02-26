"""
csv_utils.py

Helper functions for working with the CSV APOD log.
Includes duplicate detection, file checks, and display formatting.
"""

import csv

from pathlib import Path
from src.config import csv_file_path, csv_file_name, DATA_DIR
from rich.text import Text
from src.startup.console import console

HEADERS = {
    "date": "",
    "title": "",
    "url": "",
    "explanation": "",
    "logged_at": "",
    "local_file_path": "",
}


def create_csv_output_file():
    """
     Create the CSV output file if it does not already exist.

     Returns:
         None:
    """

    if check_if_csv_output_exists():
        msg = Text("\nCSV log already exists: ", style="body.text")
        msg.append(f"'{csv_file_name}'", style="app.primary")
        msg.append(". Skipping creation.", style="body.text")
        console.print(msg)
        return

    Path(csv_file_path).touch()
    write_header_to_csv()
    msg = Text("Created log file: ", style="ok")
    msg.append(f"'{csv_file_name}' ", style="app.primary")
    msg.append("✓", style="ok")
    console.print(msg)


def clear_csv_output_file():
    """
       Clear (truncate) the CSV output file contents.

       Returns:
           None:
    """

    if not check_if_csv_output_exists():
        return False

    try:
        with open(file=csv_file_path, mode='w', encoding='utf-8') as csv_file:
            viewer_dir = DATA_DIR / "viewer"
            if viewer_dir.exists() and viewer_dir.is_dir():
                for html_file in viewer_dir.glob("*.html"):
                    html_file.unlink()
            return True

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to write ", style="body.text")
        msg.append(f"'{csv_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{csv_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)
        
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return False


def delete_csv_output_file():
    """
       Delete the CSV output file from disk.

       Returns:
           None:
    """

    Path(f"{csv_file_path}").unlink()
    msg = Text("Deleted: ", style="ok")
    msg.append(f"'{csv_file_name}' ", style="app.primary")
    msg.append("✓", style="ok")
    console.print(msg)


def write_header_to_csv():
    """
    Write the CSV header row to the output file.

    Returns:
        None:
    """

    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=HEADERS.keys())
            writer.writeheader()

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to write ", style="body.text")
        msg.append(f"'{csv_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{csv_file_path}' ", style="app.primary")
        msg.append("X.", style="err")
        console.print(msg)
        
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))


def check_for_duplicate_csv_entries(formatted_apod_data):
    """
       Check whether a CSV entry with the same APOD date already exists.

       Args:
       formatted_apod_data: A dict containing the APOD snapshot to compare.

       Returns:
        bool: True if a duplicate date is found, otherwise False.
    """

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
           content = csv.reader(csv_file)

           for row in content:
              if not row or row[0] == 'date':
                  continue

              if row[0] == formatted_apod_data['date']:
                   msg = Text("Skipped (duplicate): ", style="app.secondary")
                   msg.append(str(formatted_apod_data['date']), style="app.primary")
                   msg.append(" already exists in ", style="body.text")
                   msg.append(str(csv_file_name), style="app.primary")
                   msg.append(".", style="body.text")
                   console.print(msg)
                   return True

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{csv_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{csv_file_path}' ", style="app.primary")
        msg.append("X.", style="err")
        console.print(msg)
        
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return False


def check_if_csv_output_exists():
    """
      Check whether the CSV output file exists on disk.

      Returns:
       bool: True if the file exists, otherwise False.
    """

    if Path(csv_file_path).exists() and Path(csv_file_path).is_file():
        return True

    return False


def format_raw_csv_entry(formatted_csv_entry, count):
    """
       Print a single CSV entry in a readable, numbered format.

       Args:
       formatted_csv_entry: A list representing one CSV row.
       count: Zero-based index used for display numbering.

       Returns:
        None:
    """

    console.print("─" * 60, style="app.secondary")
    print(f"Entry #{count + 1} ({formatted_csv_entry[1]}):")
    line = Text()
    line.append(f"Entry #{count + 1} ({formatted_csv_entry[1]}):\n", style="app.primary")
    line.append(f"Date: {formatted_csv_entry[0]}\n", style="body.text")
    line.append(f"Title: {formatted_csv_entry[1]}\n", style="body.text")
    line.append("URL: ", style="app.secondary")
    line.append(f"{formatted_csv_entry[2]}\n", style=f"app.url link {formatted_csv_entry[2]}")
    line.append(f"Explanation: {formatted_csv_entry[3]}\n", style="body.text")
    local_file_path = formatted_csv_entry[5] if len(formatted_csv_entry) > 5 else ""
    line.append(f"Logged_At: {formatted_csv_entry[4]}\n", style="body.text")
    line.append("Local file path: ", style="app.secondary")
    line.append(f"{local_file_path}", style="body.text")
    console.print("â”€" * 60, style="app.secondary")
    console.print(line)


def get_line_count(count):
    """
       Count the number of data rows in the CSV file.

       Args:
       count: Initial count value (typically 0).

       Returns:
        int: Total number of data rows in the file.
       """

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)
            for row in content:
                if not row or row[0] == 'date':
                    continue

                count += 1

    except PermissionError:
        msg = Text("\nPermission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{csv_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{csv_file_path}' ", style="app.primary")
        msg.append("X.", style="err")
        console.print(msg)
        
    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))

    return count
