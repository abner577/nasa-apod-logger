"""Public wallpaper API exports used by the CLI and NASA client modules."""

from src.wallpaper.service import apply_auto_wallpaper_for_single_apod, apply_auto_wallpaper_from_file_path

__all__ = ["apply_auto_wallpaper_for_single_apod", "apply_auto_wallpaper_from_file_path"]
