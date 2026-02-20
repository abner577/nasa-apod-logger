"""
nasa_date.py

Date validation helpers for NASA APOD constraints.
"""
import datetime

from src.config import NASA_APOD_START_DATE, DATE_TODAY

def check_valid_nasa_date(date_object):
    """
     Validate a date against NASA APOD availability constraints.

     Args:
     date_object: A datetime.date instance to validate.

     Returns:
        str | None: An error message if the date is invalid, otherwise None.
    """

    if date_object < NASA_APOD_START_DATE:
        return f"Input error: APOD is available starting {NASA_APOD_START_DATE}."
    elif date_object > DATE_TODAY:
        return f"Input error: Please enter a date on or before {DATE_TODAY}."

    return None

def ask_user_for_date():
    try:
        year = int(input("\nYear (YYYY): "))
        month = int(input("Month (MM): "))
        day = int(input("Day (DD): "))

    except ValueError:
        print("Invalid input. Year, month, and day must be numbers.\n")
        return None
    except Exception as e:
        print(e)
        return None

    date_object = datetime.date(year, month, day)
    check_result = check_valid_nasa_date(date_object)

    if check_result is not None:
        print(check_result)
        return None

    target_date = date_object.isoformat()
    return target_date