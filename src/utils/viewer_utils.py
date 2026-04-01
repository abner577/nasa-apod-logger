"""Utilities for building local APOD HTML viewers and viewer links."""

import html
from pathlib import Path
import os
import re
from urllib.parse import parse_qs, urlparse

from src.config import DATA_DIR


def _is_image_url(url: str) -> bool:
    lower = url.lower()
    return lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")) # if the url ends with one of these extensions, it is an image


def _is_direct_video_url(url: str) -> bool:
    """Return True when the URL path points to a direct video file."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith((".mp4", ".webm", ".mov", ".m4v", ".avi", ".mkv"))


def _is_youtube_video_url(url: str) -> bool:
    """Return True when the URL is a YouTube video URL with a detectable ID."""
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")
    is_youtube_host = (
        host == "youtu.be"
        or host.endswith(".youtube.com")
        or host == "youtube.com"
        or host.endswith(".youtube-nocookie.com")
        or host == "youtube-nocookie.com"
    )
    return is_youtube_host and bool(_extract_youtube_video_id(url))


def _extract_youtube_video_id(url: str) -> str:
    """Extract a YouTube video ID from common APOD YouTube URL formats."""
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")
    path_parts = [part for part in parsed.path.split("/") if part]

    if host == "youtu.be" and path_parts:
        candidate = path_parts[0]
    elif path_parts and path_parts[0] == "embed" and len(path_parts) > 1:
        candidate = path_parts[1]
    elif path_parts and path_parts[0] == "shorts" and len(path_parts) > 1:
        candidate = path_parts[1]
    else:
        query_params = parse_qs(parsed.query)
        candidate = query_params.get("v", [""])[0]

    match = re.match(r"^[A-Za-z0-9_-]{6,}$", candidate)
    return match.group(0) if match else ""


def _youtube_thumbnail_url(url: str) -> str:
    """Return an hq thumbnail URL for a YouTube video URL, if detectable."""
    video_id = _extract_youtube_video_id(url)
    if not video_id:
        return ""
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def _youtube_watch_url(url: str) -> str:
    """Return canonical YouTube watch URL when a video ID can be extracted."""
    video_id = _extract_youtube_video_id(url)
    if not video_id:
        return url
    return f"https://www.youtube.com/watch?v={video_id}"


def _is_wsl() -> bool:
    try:
        return "microsoft" in os.uname().release.lower() or "wsl" in os.uname().release.lower()
    except AttributeError:
        return False


def _wsl_file_uri_to_windows(uri: str) -> str:
    """
    Convert file:///mnt/<drive>/path to file:///C:/path for Windows browsers.
    If the uri doesn't match the pattern, return as-is.
    """
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
    Writes data/viewer/apod-<date>.html

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
    media_type = str(apod.get("media_type", "")).strip().lower()
    is_video = media_type == "video"
    is_youtube_video = _is_youtube_video_url(url)

    safe_title = html.escape(title)
    effective_url = _youtube_watch_url(url) if is_youtube_video else url
    safe_url = html.escape(effective_url)
    safe_explanation = html.escape(explanation)

    # print(f"Media type: {media_type}")
    # print(f"Raw url: {url}")
    # print(f"Safe url: {safe_url}")
    # print(f"Effective url: {effective_url}")

    filename = f"apod-{date}.html"
    file_path = viewer_dir / filename

    media_html = ""
    if _is_image_url(url):
        media_html = (
            f'<img id="apod-media" class="apod-image" src="{safe_url}" '
            f'alt="{safe_title}" />'
        )
    elif is_video:
        thumbnail_url = _youtube_thumbnail_url(url) if is_youtube_video else ""

        if thumbnail_url:
            safe_thumbnail_url = html.escape(thumbnail_url)
            media_html = (
                 f'<a href="{safe_url}" target="_blank" rel="noreferrer">'
                 f'<img id="apod-media" class="apod-image" src="{safe_thumbnail_url}" alt="{safe_title}" />'
                 "</a>"
             )
        elif _is_direct_video_url(url):
            media_html = (
                '<video id="apod-media" class="apod-image" controls preload="metadata">'
                f'<source src="{safe_url}">'
                "Your browser does not support the video tag."
                "</video>"
            )
        else:
            media_html = (
                '<div id="apod-media" class="apod-placeholder">'
                "<div class=\"apod-placeholder-title\">Media Preview</div>"
                f'<div class="apod-placeholder-link"><a href="{safe_url}" target="_blank" rel="noreferrer">Open APOD media</a></div>'
                "</div>"
            )
    else:
        media_html = (
            '<div id="apod-media" class="apod-placeholder">'
            "<div class=\"apod-placeholder-title\">Media Preview</div>"
            f'<div class="apod-placeholder-link"><a href="{safe_url}" target="_blank" rel="noreferrer">Open APOD media</a></div>'
            "</div>"
        )

    video_notice_html = ""
    youtube_action_html = ""

    if is_youtube_video:
        video_notice_html = (
            '<div class="video-download-notice">'
            "This APOD is hosted on YouTube, so automatic download is not available. "
            "Click the preview image or use the button below to watch it on YouTube."
            "</div>"
        )
        youtube_action_html = (
            '<a class="youtube-watch-button" '
            f'href="{safe_url}" target="_blank" rel="noreferrer">Watch on YouTube</a>'
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
      font-size: 16px;
      line-height: 1.55;
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
      font-size: 28px;
      font-weight: 700;
      letter-spacing: 0.2px;
      margin-bottom: 10px;
    }}
    .date {{
      font-size: 17px;
      font-style: italic;
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .hint {{
      font-size: 16px;
      color: var(--muted);
      margin: 10px 0 10px;
    }}
    .video-download-notice {{
      margin: 0 auto 12px;
      max-width: 760px;
      font-size: 15px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .actions {{
      margin-bottom: 18px;
    }}
    .actions a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 15px;
    }}
    .actions .youtube-watch-button {{
      display: inline-block;
      padding: 6px 13px;
      border-radius: 999px;
      border: 1px solid rgba(126, 168, 205, 0.95);
      background: linear-gradient(180deg, rgba(79, 98, 120, 0.95), rgba(52, 67, 84, 0.95));
      color: #ffffff;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.1px;
      box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.18), 0 4px 10px rgba(0, 0, 0, 0.35);
      text-decoration: none;
      transition: transform 120ms ease, filter 120ms ease;
    }}
    .actions .youtube-watch-button:visited,
    .actions .youtube-watch-button:hover,
    .actions .youtube-watch-button:active {{
      color: #ffffff;
    }}
    .actions .youtube-watch-button:hover {{
      transform: translateY(-1px);
      filter: brightness(1.06);
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
    .apod-video-link {{
      margin-top: 10px;
      font-size: 15px;
    }}
    .apod-video-link a {{
      color: var(--accent);
      text-decoration: none;
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
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 10px;
    }}
    .apod-placeholder-link a {{
      color: var(--accent);
      text-decoration: none;
      font-size: 15px;
    }}
    .apod-explanation {{
      position: absolute;
      left: 50%;
      transform: translateX(-50%) translateY(6px);
      bottom: 12px;
      width: min(720px, 88vw);
      padding: 16px 18px;
      background: var(--panel);
      color: var(--text);
      border-radius: 8px;
      text-align: left;
      font-size: 15px;
      line-height: 1.6;
      font-weight: 500;
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
    {video_notice_html}
    <div class="actions">
      {youtube_action_html}
    </div>
    <div class="media-wrap">
      {media_html}
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
