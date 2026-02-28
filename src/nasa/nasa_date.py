"""
nasa_date.py

Date validation helpers for NASA APOD constraints.
"""
from typing import Any
import datetime
from rich.text import Text
from src.startup.console import console

from src.config import NASA_APOD_START_DATE, DATE_TODAY

def check_valid_nasa_date(date_object: Any) -> Any:
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

def ask_user_for_date() -> Any:
    try:
        console.print()
        console.print(Text("Year (YYYY): ", style="app.secondary"), end="")
        year = int(input().strip())

        console.print(Text("Month (MM): ", style="app.secondary"), end="")
        month = int(input().strip())

        console.print(Text("Day (DD): ", style="app.secondary"), end="")
        day = int(input().strip())

    except ValueError:
        msg = Text("Input error: ", style="err")
        msg.append("Year, month, and day must be numbers.\n", style="body.text")
        console.print(msg)
        return None

    except Exception as e:
        console.print()
        console.print(Text(str(e), style="err"))
        return None

    try:
        date_object = datetime.date(year, month, day)
    except ValueError as e:
        console.print(Text(str(e), style="err"))
        return None

    check_result = check_valid_nasa_date(date_object)
    if check_result is not None:
        body = check_result.replace("Input error: ", "")
        msg = Text("Input error: ", style="err")


        if str(NASA_APOD_START_DATE) in body:
            before, after = body.split(str(NASA_APOD_START_DATE), 1)
            msg.append(before, style="body.text")
            msg.append(str(NASA_APOD_START_DATE), style="app.primary")
            msg.append(after, style="body.text")

        elif str(DATE_TODAY) in body:
            before, after = body.split(str(DATE_TODAY), 1)
            msg.append(before, style="body.text")
            msg.append(str(DATE_TODAY), style="app.primary")
            msg.append(after, style="body.text")
        else:
            msg.append(body, style="body.text")

        console.print(msg)
        return None

    return date_object.isoformat()