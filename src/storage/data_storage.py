"""
data_storage.py

Handles detection and creation of the application's data directory.
"""

from pathlib import Path
from src.config import DIR_PATH


def check_if_data_exists():
    """
      Check whether the application's data directory exists.

      Returns:
          bool: True if the data directory exists, otherwise False.
      """

    if Path(f"{DIR_PATH}/data").is_dir():
        return True
    else:
        return False


def create_data_directory():
    """
      Create the application's data directory if it does not already exist.

      Returns:
        None:
      """

    if check_if_data_exists():
        print("Directory 'data' already exists ❌")
        return

    Path(f"{DIR_PATH}/data").mkdir(parents=True, exist_ok=True)
    print("Directory 'data' created ✅")



