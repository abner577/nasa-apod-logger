"""
config.py

Centralized configuration and constant values for the application.
All values defined here are intended to be imported and reused across modules.
"""

import datetime

DIR_PATH = "C://Users/joser/PycharmProjects/NASA-APOD-Logger"

json_file_path = f"{DIR_PATH}/data/output.jsonl"
json_file_name = "output.jsonl"

csv_file_path = f"{DIR_PATH}/data/output.csv"
csv_file_name = "output.csv"

NASA_APOD_START_DATE = datetime.date(1995, 6, 16)
DATE_TODAY = datetime.date.today()

