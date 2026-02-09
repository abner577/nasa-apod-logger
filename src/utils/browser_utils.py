import os
import shutil
import subprocess
import webbrowser

"""
browser_utils.py

Browser-related helper utilities for user navigation.
"""

def _is_wsl() -> bool:
    # WSL detection
    try:
        return "microsoft" in os.uname().release.lower() or "wsl" in os.uname().release.lower()
    except AttributeError:
        return False


def take_user_to_browser(url: str) -> None:
    """
    Open the APOD URL in the user's default web browser.

    Returns:
        None
    """
    try:
        # If running in WSL, use Windows to open the URL
        if _is_wsl():
            if shutil.which("wslview"):
                subprocess.run(["wslview", url], check=False)
                return

            # Fallback: Windows start command
            subprocess.run(["cmd.exe", "/c", "start", "", url], check=False)
            return

        print(f"Opening in browser 🌐: {url}")
        webbrowser.open_new_tab(url)

    except Exception as e:
        print(f"Browser error: Unable to open the link. ({e})")
        print(f"URL: {url}")
