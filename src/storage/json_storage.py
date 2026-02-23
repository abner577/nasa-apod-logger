"""
json_storage.py

JSONL persistence layer for APOD snapshots.
Responsible for creating, writing, reading, and rewriting the JSONL log.
"""

from src.utils.json_utils import *
from src.utils.data_utils import *
from src.nasa.nasa_date import check_valid_nasa_date
from src.config import json_file_path, json_file_name, NASA_APOD_START_DATE, DATE_TODAY
from rich.text import Text
from src.startup.console import console


def log_data_to_json(formatted_apod_data):
    """
       Append a formatted APOD snapshot to the JSONL log.

       Args:
       formatted_apod_data: A dict containing the snapshot fields to write.

       Returns:
        None:
    """

    if not check_if_json_output_exists():
        return None

    if check_for_duplicate_json_entries(formatted_apod_data):
        return "Duplicate found."

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            # One JSON object per line so we can safely append.
            # Need to use .dumps to write JSON as a string
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")

            msg = Text("Saved: ", style="ok")
            msg.append("APOD ", style="body.text")
            msg.append(f"'{formatted_apod_data['date']}'", style="app.primary")
            msg.append(" -> ", style="body.text")
            msg.append(f"{json_file_name} ", style="app.primary")
            msg.append("✓", style="ok")
            console.print(msg)

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to write ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))

    return None


def show_first_n_json_log_entries():
    """
        Display the first N logged JSONL entries.

        Args:
        entries_amount: Number of entries to display.

        Returns:
         None:
    """

    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        console.print(Text("Input error: ", style="err").append("Enter a valid number.", style="body.text"))
        console.print()
        return
    
    except Exception as e:
        console.print(Text(str(e), style="err"))
        return

    if entries_amount < 1:
        console.print(Text("Input error: ", style="err").append("Enter a number of 1 or more.", style="body.text"))
        console.print()
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(0)

    if line_count == 0:
        console.print(Text("\nNo entries found.\n", style="body.text"))
        return

    if entries_amount > line_count:
        msg = Text("Only ", style="body.text")
        msg.append(str(line_count), style="app.primary")
        msg.append(" entries available. Showing all.\n", style="body.text")
        console.print(msg)

        entries_amount = line_count
    count = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                # Need to use .loads to convert JSON string --> dict
                # Since we used .dumps we need to use .loads to read the proper format
                content = json.loads(line)
                format_raw_jsonl_entry(content, count)
                count += 1
                if count == entries_amount:
                    break

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        msg = Text("JSONL parse error: ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))


def show_last_n_json_log_entries():
    """
    Display the last N logged JSONL entries.

       Args:
    entries_amount: Number of entries to display.

       Returns:
        None:
    """

    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        console.print(Text("Input error: ", style="err").append("Enter a valid number.", style="body.text"))
        console.print()
        return

    except Exception as e:
        console.print(Text(str(e), style="err"))
        return

    if entries_amount < 1:
        console.print(Text("Input error: ", style="err").append("Enter a number of 1 or more.", style="body.text"))
        console.print()
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(count=0)

    if line_count == 0:
        console.print(Text("\nNo entries found.\n", style="body.text"))
        return

    if entries_amount > line_count:
        msg = Text("Only ", style="body.text")
        msg.append(str(line_count), style="app.primary")
        msg.append(" entries available. Showing all.\n", style="body.text")
        console.print(msg)
        entries_amount = line_count

    count = 0
    entries_list = []

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                entries_list.append(content)
                count += 1

                if count > entries_amount:
                    entries_list.remove(entries_list[0])
                    count -= 1

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)
        return

    except json.decoder.JSONDecodeError:
        msg = Text("JSONL parse error: ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)
        return

    except Exception as e:
        console.print(Text(str(e), style="err"))
        return

    count = 0
    for entry in entries_list:
        format_raw_jsonl_entry(entry, count)
        count += 1


def show_all_json_entries():
    """
        Display all logged JSONL entries.

    Returns:
        None:
    """

    if not check_if_json_output_exists():
        return

    count = 0
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                format_raw_jsonl_entry(content, count)
                count += 1

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        msg = Text("JSONL parse error: ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))

    if count == 0:
        console.print(Text("\nNo entries found.\n", style="body.text"))
        return


def delete_one_json_entry(target_date):
    """
       Delete a single JSONL entry by its APOD date.

       Prompts the user for a date, removes the matching JSON object, and rewrites
       the JSONL file with the remaining entries.

       Returns:
        Boolean:
    """

    entries_to_keep = []

    if not check_if_json_output_exists():
        return False

    found = False

    try:
        # Read phase
        # Need to rewrite the entire file: you can't delete a single JSONL line in-place safely.
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] == target_date:
                    found = True

                else:
                    entries_to_keep.append(content)

            if not found:
                msg = Text("\nNo entry found for ", style="body.text")
                msg.append(str(target_date), style="app.primary")
                msg.append(" ", style="body.text")
                msg.append("X\n", style="err")
                console.print(msg)
                return False

            # Write phase
            with open(file=json_file_path, mode='w') as file:
                for entry in entries_to_keep:
                    file.write(json.dumps(entry, ensure_ascii=False) + "\n")

            return True

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
        msg = Text("JSONL parse Error : ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}' ", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))


def fetch_most_recent_json_apod():
    """
         Fetch the most recent APOD (by date) from the jsonl log.
         Doesn't matter in which order it was logged.
         Ex: Todays APOD will always be the most recent.

         Returns:
             None:
    """
    if not check_if_json_output_exists():
        return

    most_recent_date = NASA_APOD_START_DATE.isoformat()
    most_recent_apod = None

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] >= most_recent_date:
                    most_recent_date = content['date']
                    most_recent_apod = content

            if most_recent_apod is None:
                msg = Text("\nNo entries found in ", style="body.text")
                msg.append(json_file_name, style="app.primary")
                msg.append(".\n", style="body.text")
                console.print(msg)
                return

            most_recent_apod = format_apod_data(most_recent_apod)
            print()
            format_raw_jsonl_entry(most_recent_apod, 0)

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
        msg = Text("JSONL parse Error : ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}' ", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))


def fetch_oldest_json_apod():
    """
        Fetch the oldest APOD (by date) from the CSV log.
        Doesn't matter in which order it was logged.
        Ex: First APOD ever uploaded will always be the oldest.

        Returns:
            None:
    """

    if not check_if_json_output_exists():
        return

    oldest_date = DATE_TODAY.isoformat()
    oldest_apod = None

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)

                if content['date'] <= oldest_date:
                    oldest_date = content['date']
                    oldest_apod = content

            if oldest_apod is None:
                print(f"{json_file_name} is empty.")
                return

            oldest_apod = format_apod_data(oldest_apod)
            print()
            format_raw_jsonl_entry(oldest_apod, 0)

    except PermissionError:
        msg = Text("Permission error: ", style="err")
        msg.append("Unable to read/write ", style="body.text")
        msg.append(f"'{json_file_name}'", style="app.primary")
        msg.append(" at ", style="body.text")
        msg.append(f"'{json_file_path}' ", style="app.primary")
        msg.append("X", style="err")
        console.print(msg)

    except json.decoder.JSONDecodeError:
        print(f"JSONL parse Error: Could not decode JSON from file '{json_file_name}'. Check the file format.")
        msg = Text("JSONL parse Error : ", style="err")
        msg.append("Could not decode JSON from file ", style="body.text")
        msg.append(f"'{json_file_name}' ", style="app.primary")
        msg.append(". Check the file format.", style="body.text")
        console.print(msg)

    except Exception as e:
        console.print(Text(str(e), style="err"))


def log_multiple_json_entries(list_formatted_apod_data):
    """
       Log multiple APOD entries to jsonl.

       Returns:
           None:
    """
    for entry in list_formatted_apod_data:
        log_data_to_json(entry)