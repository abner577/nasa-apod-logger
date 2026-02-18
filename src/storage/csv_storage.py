"""
csv_storage.py

CSV persistence layer for APOD snapshots.
Responsible for creating, writing, reading, and rewriting the CSV log.
"""

from src.utils.csv_utils import *
from src.utils.data_utils import *
from src.config import csv_file_path, csv_file_name, NASA_APOD_START_DATE, DATE_TODAY
from src.nasa.nasa_date import check_valid_nasa_date


def log_data_to_csv(formatted_apod_data):
    """
       Append a formatted APOD snapshot to the CSV log.

       Args:
    formatted_apod_data: A dict containing the snapshot fields to write.

       Returns:
        None:
    """

    if not check_if_csv_output_exists():
        return

    if check_for_duplicate_csv_entries(formatted_apod_data):
        return

    try:
        with open(file=csv_file_path, mode='a', encoding='utf-8', newline="") as csv_file:
            # newline="" prevents extra blank lines on Windows when writing CSV.
            # DictWriter writes dict values in the exact order of fieldnames.
            writer = csv.DictWriter(csv_file, fieldnames=formatted_apod_data.keys())
            writer.writerow(formatted_apod_data)
            print(f"Saved: APOD '{formatted_apod_data['date']}' -> {csv_file_name} ✓")

    except PermissionError:
        print(f"Permission error: Unable to write '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)


def show_first_n_csv_log_entries():
    """
     Display the first N logged CSV entries.

     Args:
    entries_amount: Number of entries to display.

     Returns:
        None:
    """
    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        print("Input error: Enter a valid number.\n")
        return
    except Exception as e:
        print(e)
        return


    if entries_amount < 1:
        print("Input error: Enter a number of 1 or more.\n")
        return

    if not check_if_csv_output_exists():
        return

    line_count = get_line_count(count=0)

    if line_count == 0:
        print("\nNo entries found.\n")
        return

    if entries_amount > line_count:
        print(f"Only {line_count} entries available. Showing all.\n")
        entries_amount = line_count
    count = 0

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)

            for row in content:
                if not row or row[0] == 'date':
                    continue

                format_raw_csv_entry(row, count)
                count += 1
                if count == entries_amount:
                    break


    except PermissionError:
        print(f"Permission error: Unable to read '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)


def show_last_n_csv_log_entries():
    """
        Display the last N logged CSV entries.

        Args:
        entries_amount: Number of entries to display.

        Returns:
            None:
    """

    try:
        entries_amount = int(input("\nEnter number of entries: "))

    except ValueError:
        print("Input error: Enter a valid number.\n")
        return
    except Exception as e:
        print(e)
        return

    entries_list = []

    if entries_amount < 1:
        print("Input error: Enter a number of 1 or more.\n")
        return

    if not check_if_csv_output_exists():
        return

    line_count = get_line_count(count=0)

    if line_count == 0:
        print("N\nNo entries found.\n")
        return

    if entries_amount > line_count:
        print(f"Only {line_count} entries available. Showing all.\n")
        entries_amount = line_count
    count = 0

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)

            for row in content:
                if not row or row[0] == 'date':
                    continue

                entries_list.append(row)
                count += 1

                if count > entries_amount:
                    entries_list.remove(entries_list[0])
                    count -= 1

    except PermissionError:
        print(f"Permission error: Unable to read '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)

    count = 0
    for entry in entries_list:
        format_raw_csv_entry(entry, count)
        count += 1


def show_all_csv_entries():
    """
      Display all logged CSV entries.

      Returns:
          None:
    """

    if not check_if_csv_output_exists():
        return

    count = 0
    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)

            for row in content:
                if not row or row[0] == 'date':
                    continue

                format_raw_csv_entry(row, count)
                count += 1


    except PermissionError:
        print(f"Permission error: Unable to read '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)

    if count == 0:
        print("\nNo entries found.\n")
        return


def delete_one_csv_entry():
    """
        Delete a single CSV entry by its APOD date.

        Prompts the user for a date, removes the matching row, and rewrites the
        CSV file with the remaining entries.

        Returns:
            None:
    """

    entries_to_keep = []

    if not check_if_csv_output_exists():
        return

    try:
        year = int(input("\nYear (YYYY): "))
        month = int(input("Month (MM): "))
        day = int(input("Day (DD): "))

    except ValueError:
        print("Input error: Year, month, and day must be numbers.\n")
        return
    except Exception as e:
        print(e)
        return

    date_object = datetime.date(year, month, day)
    check_result = check_valid_nasa_date(date_object)

    if check_result is not None:
        print(check_result)
        return


    target_date = date_object.isoformat()
    found = False

    try:
        # Read phase
        with open(csv_file_path, mode="r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                if row["date"] == target_date:
                    found = True
                    continue
                entries_to_keep.append(row)

        if not found:
            print("\nNo entry found for {target_date} X\n")
            return

        # Write phase
        with open(csv_file_path, mode="w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=reader.fieldnames)

            writer.writeheader()
            writer.writerows(entries_to_keep)

        print(f"\nDeleted entry: {target_date} ✓\n")

    except PermissionError:
        print(f"Permission error: Unable to read/write '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)


def fetch_most_recent_csv_apod():
    """
      Fetch the most recent APOD (by date) from the CSV log.
      Doesn't matter in which order it was logged.
      Ex: Todays APOD will always be the most recent.

      Returns:
          None:
      """

    if not check_if_csv_output_exists():
        return

    most_recent_date = NASA_APOD_START_DATE.isoformat()
    most_recent_apod = None

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)
            for row in content:
                if not row or row[0] == 'date':
                    continue

                if row[0] >= most_recent_date:
                    most_recent_date = row[0]
                    most_recent_apod = row

            if most_recent_apod is None:
                print(f"\nNo entries found in {csv_file_name}.\n")
                return

            print()
            format_raw_csv_entry(most_recent_apod, 0)

    except PermissionError:
        print(f"Permission error: Unable to read '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)


def fetch_oldest_csv_apod():
    """
        Fetch the oldest APOD (by date) from the CSV log.
        Doesn't matter in which order it was logged.
        Ex: First APOD ever uploaded will always be the oldest.

        Returns:
            None:
    """

    if not check_if_csv_output_exists():
        return

    oldest_date = DATE_TODAY.isoformat()
    oldest_apod = None

    try:
        with open(file=csv_file_path, mode='r', encoding='utf-8') as csv_file:
            content = csv.reader(csv_file)
            for row in content:
                if not row or row[0] == 'date':
                    continue

                if row[0] >= oldest_date:
                    oldest_date = row[0]
                    oldest_apod = row

            if oldest_apod is None:
                print(f"nNo entries found in {csv_file_name}.\n")
                return

            print()
            format_raw_csv_entry(oldest_apod, 0)

    except PermissionError:
        print(f"Permission error: Unable to read '{csv_file_name}' at '{csv_file_path}' X")
    except Exception as e:
        print(e)


def log_multiple_csv_entries(list_formatted_apod_data):
    """
       Log multiple APOD entries to csv.

       Returns:
           None:
    """
    for entry in list_formatted_apod_data:
        log_data_to_csv(entry)