from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

STARTUP_ARTS_THEME = Theme({

    # Identity
    "app.primary": "color(69)",       # blue for app primary color
    "app.secondary": "color(29)",     # green for app secondary color

    "body.text": "color(252)",  # gray-white for body text

    "ok": "color(40)",  # GREEN for ✓
    "err": "color(160)",  # RED for X & errors

    # ----------------------- STARTUP ARTS -----------------------

    # SPACE STARTUP ART
    "border.frame": "dim color(97)",  # navy-black / deep space blue
    "planet.glow": "dim color(39)",  # cool cyan glow

    # SPACESHIP STARTUP ARTS
    "ship.body": "color(252)",  # light gray hull
    "ship.trim": "color(250)",  # slightly darker trim
    "ship.usa": "bold color(160)",  # bright red
    "ship.flame.outer": "bold color(160)",  # bright red flame edge
    "ship.flame.inner": "color(214)",  # orange-yellow flame core

    "ship.dots": "color(37)",  # teal / cyan dots
    "ship.paren": "bold color(93)",  # bold purple accents
    "ship.nasa.red": "bold color(160)",  # NASA red
    "ship.nasa.blue": "bold color(39)",  # NASA blue

    # MOON STARTUP ART
    "sun.primary": "bold color(220)",  # warm yellow / sun glow
    "star.purple": "color(93)",  # purple star
    "star.blue": "color(39)",  # blue star
    "star.muted": "dim color(250)",  # faint gray star
    "moon.body": "color(252)",  # light gray moon surface
    "nasa.red": "bold color(160)",  # NASA red
    "nasa.blue": "bold color(27)",  # NASA deep blue

    # ASTRONAUTS STARTUP ARTS
    "flag.canton": "bold color(33)",  # deep blue flag canton
    "flag.stripe.red": "bold color(160)",  # red stripes
    "flag.stripe.white": "color(252)",  # white stripes
    "pole.body": "color(245)",  # muted gray pole
    "pole.top": "bold color(220)",  # gold/yellow finial
    "astronaut.body": "color(152)",  # pale blue suit body
    "astronaut.detail": "dim color(109)",  # muted teal details
    "ground": "color(97)",  # dark navy ground
    "usa.red": "bold color(160)",  # USA red
    "usa.blue": "bold color(39)",  # USA blue

    "astro.body": "color(153)",  # soft light blue
    "astro.metal": "color(245)",  # dull metallic gray

    # ALIEN STARTUP ARTS
    "alien.symbol.caret": "bold color(63)",  # neon cyan-green
    "alien.symbol.plus": "bold color(98)",  # electric purple
    "alien.eyes": "bold color(40)",  # bright green

    # Fire (red -> orange -> yellow + sparks)
    "fire.red": "color(160)",  # bright red flame
    "fire.orange": "color(208)",  # orange flame
    "fire.spark": "color(226)",  # bright spark yellow

    # Alien (sickly)
    "alien.body": "color(118)",  # sickly green

    # SATELLITE STARTUP ART
    "sat.metal": "bold color(230)",  # warm cream satellite body
    "sat.light": "bold color(220)",  # warm gold ground/platform
})

console = Console(theme=STARTUP_ARTS_THEME, highlight=False)