
from src.storage.data_storage import DIR_PATH
from src.utils.json_utils import *
from src.utils.data_utils import *

json_file_path = f"{DIR_PATH}/data/output.jsonl"
json_file_name = "output.jsonl"
NASA_APOD_START_DATE = datetime.date(1995, 6, 16)


def create_json_output_file():
    if check_if_json_output_exists():
        print(f"Cannot create file at '{json_file_path}' because it already exists ❌")
        return

    Path(f"{json_file_path}").touch()
    print(f"output.jsonl file created at '{json_file_path}' ✅")


def log_data_to_json(formatted_apod_data):
    if not check_if_json_output_exists():
        return

    if check_for_duplicate_json_entries(formatted_apod_data):
        return

    try:
        with open(file=json_file_path, mode='a', encoding='utf-8') as json_file:
            json_file.write(json.dumps(formatted_apod_data, ensure_ascii=False) + "\n")
            print(f"Successfully logged data to '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def clear_json_output_file():
    if not check_if_json_output_exists():
        return

    try:
        with open(file=json_file_path, mode='w') as json_file:
            print(f"Successfully cleared file: '{json_file_name}' ✅")

    except PermissionError:
        print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
    except Exception as e:
        print(e)


def delete_json_output_file():
    Path(f"{json_file_path}").unlink()
    print(f"File: {json_file_name} at path: '{json_file_path}' deleted ✅.")


def show_first_n_json_log_entries(entries_amount):
    if entries_amount < 1:
        print("Amount of entries cannot be less than 1.")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(0)

    if entries_amount > line_count:
        print(f"We only have {line_count} entries in total. Displaying all the entries that we have...")
        entries_amount = line_count

    count = 0

    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                format_raw_jsonl_entry(content, count)
                count += 1
                if count == entries_amount:
                    break

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)


def show_last_n_json_log_entries(entries_amount):
    entries_list = []

    if entries_amount < 1:
        print("Amount of entries cannot be less than 1.")
        return

    if not check_if_json_output_exists():
        return

    line_count = get_line_count(count=0)

    if entries_amount > line_count:
        print(f"We only have {line_count} entries in total. Displaying all the entries that we have...")
        entries_amount = line_count

    count = 0

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
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)

    count = 0
    for entry in entries_list:
        format_raw_jsonl_entry(entry, count)
        count += 1


def fetch_most_recent_json_apod():
    pass


def fetch_oldest_json_apod():
    pass


def show_all_json_entries():
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
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)


def delete_one_json_entry():
    entries_to_keep = []

    if not check_if_json_output_exists():
        pass

    year = int(input("Enter a year (YYYY): "))
    month = int(input("Enter a month (MM): "))
    day = int(input("Enter a day (DD): "))

    date_object = datetime.date(year, month, day)
    date_today = datetime.date.today()

    if date_object < NASA_APOD_START_DATE:
        print("⚠️ Please enter a date after June 16, 1995")
    elif date_object > date_today:
        print(f"⚠️ Please enter a date before {date_today}")

    count = 0
    try:
        with open(file=json_file_path, mode='r') as json_file:
            for line in json_file:
                if line is None or len(line) == 0:
                    continue

                content = json.loads(line)
                count += 1

                if content['date'] == date_object.isoformat():
                    print(f"This entry has been found ✅.")

                else:
                    entries_to_keep.append(content)

            if count == len(entries_to_keep):
                print(f"This entry was not found ❌.")
                return

            else:
                print("Removing entry...")
                try:
                    with open(file=json_file_path, mode='w') as file:
                        for entry in entries_to_keep:
                            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

                except PermissionError:
                    print(f"Dont have permission to write to file: '{json_file_name}' at path: '{json_file_path}'.")
                except Exception as e:
                    print(e)

    except PermissionError:
        print(f"Dont have permission to read file: '{json_file_name}' at path: '{json_file_path}'.")
    except json.decoder.JSONDecodeError:
        print(f"Could not decode JSON from file '{json_file}'. Check the file format.")
    except Exception as e:
        print(e)



