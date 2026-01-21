import webbrowser

"""
browser_utils.py

Browser-related helper utilities for user navigation.
"""

def take_user_to_browser(url):
    """
      Open the APOD URL in the user's default web browser.

      Returns:
       None:
    """  # For Windows

    try:
        print(f"Opening in browser 🌐: {url}")
        webbrowser.open_new_tab(url)

    except webbrowser.Error:
        print("Browser error: Unable to open the link in a new tab.")
