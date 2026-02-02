from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

DEEP_SPACE_THEME = Theme({
    # Identity
    "app.title": "bold color(39)",      # light blue
    "app.banner": "bold color(27)",     # deep blue
    "accent": "color(93)",              # purple

    # Text hierarchy
    "body": "color(252)",               # light gray
    "muted": "dim color(250)",
    "label": "bold color(39)",
    "value": "color(252)",

    # Status
    "ok": "bold color(37)",              # teal
    "warn": "bold yellow",
    "err": "bold red",

    # UI
    "rule": "dim color(27)",
    "menu.key": "bold color(39)",
    "menu.text": "color(252)",

    # SPACE_STARTUP_ART_1
    "earth.land": "color(34)",       # dark green
    "earth.water": "on color(25)",   # muted blue ocean

    # SPACESHIP_STARTUP_ART1
   "ship.body": "color(252)",
   "ship.trim": "color(250)",
   "ship.window": "color(39)",
   "ship.panel": "color(27)",
   "ship.usa": "bold color(160)",
   "ship.flame.outer": "bold color(160)",
   "ship.flame.inner": "color(214)",

  "ship.dots": "color(37)",
  "ship.paren": "bold color(93)",
  "ship.nasa.red": "bold color(160)",
  "ship.nasa.blue": "bold color(39)",

})

console = Console(theme=DEEP_SPACE_THEME)