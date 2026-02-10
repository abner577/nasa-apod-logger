"""
nasa_date.py

Date validation helpers for NASA APOD constraints.
"""

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
        return f"Invalid date: APOD is available starting {NASA_APOD_START_DATE}."
    elif date_object > DATE_TODAY:
        return f"Invalid date: Please enter a date on or before {DATE_TODAY}."

    return None
