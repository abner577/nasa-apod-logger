"""
data_storage.py

Handles detection and creation of the application's data directory.
"""
from typing import Any

from src.config import DATA_DIR


def check_if_data_exists() -> Any:
    return DATA_DIR.is_dir()


def create_data_directory() -> Any:
    if check_if_data_exists():
        print("Data directory already exists. Skipping creation.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("\nCreated data directory v")