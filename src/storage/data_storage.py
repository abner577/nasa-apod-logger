"""
data_storage.py

Handles detection and creation of the application's data directory.
"""

from src.config import DATA_DIR


def check_if_data_exists():
    """
      Check whether the application's data directory exists.

      Returns:
          bool: True if the data directory exists, otherwise False.
    """

    return DATA_DIR.is_dir()


def create_data_directory():
    """
      Create the application's data directory if it does not already exist.

      Returns:
        None:
    """

    if check_if_data_exists():
        print("Data directory already exists. Skipping creation.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("\nCreated data directory v")