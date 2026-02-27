import html
from pathlib import Path
import os

from src.config import DATA_DIR

"""
viewer_utils.py

Utilities for generating local HTML viewer pages for APOD entries.
"""


def _is_image_url(url: str) -> bool:
    lower = url.lower()
    return lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")) # if the url ends with one of these extensions, it is an image


def _is_wsl() -> bool:
    try:
        return "microsoft" in os.uname().release.lower() or "wsl" in os.uname().release.lower()
    except AttributeError:
        return False


# This method just converts the wsl file path to the actual file path (not using the mnt prefix)
def _wsl_file_uri_to_windows(uri: str) -> str:
    prefix = "file:///mnt/"
    if not uri.startswith(prefix) or len(uri) <= len(prefix):
        return uri

    drive_letter = uri[len(prefix)]
    if drive_letter < "a" or drive_letter > "z":
        return uri

    rest = uri[len(prefix) + 1:]
    return f"file:///{drive_letter.upper()}:{rest}"


def viewer_path_to_uri(path: Path) -> str:
    uri = path.as_uri()
    if _is_wsl():
        return _wsl_file_uri_to_windows(uri)
    return uri


def build_apod_viewer(apod: dict) -> Path:
    """
    Create a local HTML viewer for a formatted APOD entry.

    Args:
        apod: Formatted APOD dict with keys: date, title, url, explanation.

    Returns:
        Path to the generated HTML file.
    """
    viewer_dir = DATA_DIR / "viewer"
    viewer_dir.mkdir(parents=True, exist_ok=True)

    date = apod.get("date", "unknown-date")
    title = apod.get("title", "NASA APOD")
    url = apod.get("url", "")
    explanation = apod.get("explanation", "")

    safe_title = html.escape(title)
    safe_url = html.escape(url)
    safe_explanation = html.escape(explanation)

    download_label = "Save this APOD media"
    if not _is_image_url(url):
        download_label = "Open source media"

    filename = f"apod-{date}.html"
    file_path = viewer_dir / filename

    image_html = ""
    if _is_image_url(url):
        image_html = (
            f'<img id="apod-media" class="apod-image" src="{safe_url}" '
            f'alt="{safe_title}" />'
        )
    else:
        image_html = (
            '<div id="apod-media" class="apod-placeholder">'
            "<div class=\"apod-placeholder-title\">Media Preview</div>"
            f'<div class="apod-placeholder-link"><a href="{safe_url}" target="_blank" rel="noreferrer">Open APOD media</a></div>'
            "</div>"
        )

    html_content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title} | APOD</title>
  <style>
    :root {{
      --bg: #2f3136;
      --panel: rgba(20, 20, 20, 0.8);
      --text: #f0f0f0;
      --muted: #cfcfcf;
      --accent: #9ad0ff;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 32px 16px;
      box-sizing: border-box;
    }}
    .container {{
      max-width: 960px;
      width: 100%;
      text-align: center;
    }}
    .title {{
      font-size: 24px;
      margin-bottom: 8px;
    }}
    .date {{
      font-size: 14px;
      color: var(--muted);
      margin-bottom: 16px;
    }}
    .hint {{
      font-size: 13px;
      color: var(--muted);
      margin: 10px 0 8px;
    }}
    .actions {{
      margin-bottom: 16px;
    }}
    .actions a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 14px;
    }}
    .media-wrap {{
      display: inline-block;
      position: relative;
      max-width: 100%;
    }}
    .apod-image {{
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .apod-placeholder {{
      width: min(640px, 90vw);
      height: 360px;
      border-radius: 8px;
      background: #1c1c1c;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .apod-placeholder-title {{
      font-size: 18px;
      margin-bottom: 8px;
    }}
    .apod-placeholder-link a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 14px;
    }}
    .apod-explanation {{
      position: absolute;
      left: 50%;
      transform: translateX(-50%) translateY(6px);
      bottom: 12px;
      width: min(720px, 88vw);
      padding: 14px 16px;
      background: var(--panel);
      color: var(--text);
      border-radius: 8px;
      text-align: left;
      opacity: 0;
      pointer-events: none;
      transition: opacity 120ms ease, transform 120ms ease;
    }}
    .apod-explanation.visible {{
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="title">{safe_title}</div>
    <div class="date">{html.escape(date)}</div>
    <div class="hint">Hover the image to see the explanation.</div>
    <div class="actions">
      <a href="{safe_url}" target="_blank" rel="noreferrer" download="apod-{html.escape(date)}">{download_label}</a>
      <div class="hint">If download does not start automatically, open the media and save manually.</div>
    </div>
    <div class="media-wrap">
      {image_html}
      <div id="apod-explanation" class="apod-explanation">{safe_explanation}</div>
    </div>
  </div>

  <script>
    (function() {{
      var media = document.getElementById("apod-media");
      var explanation = document.getElementById("apod-explanation");
      if (!media || !explanation) return;
      media.addEventListener("mouseenter", function() {{
        explanation.classList.add("visible");
      }});
      media.addEventListener("mouseleave", function() {{
        explanation.classList.remove("visible");
      }});
    }})();
  </script>
</body>
</html>
"""

    file_path.write_text(html_content, encoding="utf-8")
    return file_path
