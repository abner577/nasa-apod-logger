from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

STARTUP_ARTS_THEME = Theme({
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

    # SPACE STARTUP ARTS
    "earth.land": "color(34)",       # dark green
    "earth.water": "on color(25)",   # muted blue ocean

    "border.frame": "dim color(97)"  ,    # navy-black  # deep space blue,  # soft graphite
    "planet.core": "bold color(252)",     # light gray body
    "planet.ridge": "color(250)",         # slightly darker contour
    "planet.glow": "dim color(39)",       # cool cyan glow

    # SPACESHIP STARTUP ARTS
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

    # MOON STARTUP ART
   "sun.primary": "bold color(220)",
   "star.purple": "color(93)",
   "star.blue": "color(39)",
   "star.muted": "dim color(250)",
   "moon.body": "color(252)",
   "nasa.red": "bold color(160)",
   "nasa.blue": "bold color(27)",

    # ASTRONAUTS STARTUP ARTS
   "flag.canton": "bold color(33)",
   "flag.stripe.red": "bold color(160)",
   "flag.stripe.white": "color(252)",
   "pole.body": "color(245)",
   "pole.top": "bold color(220)",
   "astronaut.body": "color(152)",
   "astronaut.detail": "dim color(109)",
   "ground": "color(97)",
   "usa.red": "bold color(160)",
   "usa.blue": "bold color(39)",

   "astro.body": "color(153)",
   "astro.metal": "color(245)",
   "astro.highlight": "color(252)",

    # ALIEN STARTUP ARTS
   "alien.symbol.caret": "bold color(63)",
   "alien.symbol.plus": "bold color(98)",
   "alien.eyes": "bold color(40)",

    # Astronaut
    "astro.suit": "color(252)",
    "astro.suit.dim": "dim color(250)",
    "astro.detail": "dim color(245)",
    "astro.joint": "color(246)",
    "astro.visor": "bold color(39)",

    # Gun
    "gun.body": "bold color(82)",
    "gun.detail": "color(70)",

    # Fire (red -> orange -> yellow + sparks)
    "fire.red": "color(160)",
    "fire.orange": "color(208)",
    "fire.yellow": "color(220)",
    "fire.spark": "color(226)",

    # Alien (sickly)
    "alien.body": "color(118)",

    # SATELLITE STARTUP ART
    "sat.metal": "bold color(230)",   # warm cream
    "sat.light": "bold color(220)",  # warm gold
    "sat.dark": "dim color(94)",      # bronze/brown shadow
})

console = Console(theme=STARTUP_ARTS_THEME)