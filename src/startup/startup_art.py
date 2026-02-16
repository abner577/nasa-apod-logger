from rich.text import Text
from src.startup.console import console
from src.config import *
import random


def startup_banner1():
    banner = r"""
 __   __     ______     ______     ______        ______     ______   ______     _____          
/\ "-.\ \   /\  __ \   /\  ___\   /\  __ \      /\  __ \   /\  == \ /\  __ \   /\  __-.      
\ \ \-.  \  \ \  __ \  \ \___  \  \ \  __ \     \ \  __ \  \ \  _-/ \ \ \/\ \  \ \ \/\ \   
 \ \_\\"\_\  \ \_\ \_\  \/\_____\  \ \_\ \_\     \ \_\ \_\  \ \_\    \ \_____\  \ \____-    
  \/_/ \/_/   \/_/\/_/   \/_____/   \/_/\/_/      \/_/\/_/   \/_/     \/_____/   \/____/
     __         ______     ______     ______     ______     ______    
    /\ \       /\ __  \   /\  ___\   /\  ___\   /\  ___\   /\  == \   
    \ \ \____  \ \ \/\ \  \ \ \__ \  \ \ \__ \  \ \  __\   \ \  __<   
     \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\ 
      \/_____/   \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/                                                                                                                   
        """
    console.print(banner, style="accent")


def render_space_startup_art_1() -> None:
    char_style_map = {
        "{": "border.frame",
        "}": "border.frame",

        "O": "sun.primary",
        "-": "sun.primary",
        "|": "sun.primary",

        "*": "star.purple",
        "D": "star.blue",

        "_": "planet.glow",
        "/": "planet.glow",
        "\\": "planet.glow",

        "~": "sun.primary",

        "`": "planet.glow",
        "'": "planet.glow",
        ",": "planet.glow",
        ".": "planet.glow",
    }

    randomized_chars = {"@", "+", "o", ".", "=", ")", ">", "<"}

    text = Text()
    for line_idx, line in enumerate(SPACE_STARTUP_ART_1.splitlines()):
        if line_idx > 0:
            text.append("\n")

        for ch in line:
            if ch in randomized_chars:
                # randomized colors for the following chars
                text.append(ch, style=random.choice(["star.purple", "star.blue"]))
                continue

            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)


def render_spaceship_startup_art_1() -> None:
    char_style_map = {
        "^": "ship.flame.inner",
        "(": "ship.flame.outer",
        ")": "ship.flame.outer",
        ":": "ship.flame.inner",
        ".": "ship.flame.inner",
        "|": "ship.trim",

        "/": "ship.trim",
        "\\": "ship.trim",
        "_": "ship.trim",
        "=": "ship.trim",
        "!": "ship.flame.inner",
        "#": "ship.trim",

        "U": "ship.usa",
        "S": "ship.usa",
        "A": "ship.usa",
    }

    text = Text()

    for line_index, line in enumerate(SPACESHIP_STARTUP_ART_1.splitlines()):
        if line_index > 0:
            text.append("\n")

        for ch in line:
            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)


def render_spaceship_startup_art_2() -> None:
    char_style_map = {
        "/": "ship.body",
        "\\": "ship.body",
        "|": "ship.body",
        "-": "ship.body",
        "_": "ship.nasa.blue",
        "!": "ship.nasa.red",

        ".": "ship.dots",
        "(": "ship.paren",
        ")": "ship.paren",

        "N": "ship.nasa.red",
        "S": "ship.nasa.red",
        "A": "ship.nasa.blue",
    }

    text = Text()

    for line_index, line in enumerate(SPACESHIP_STARTUP_ART_2.splitlines()):
        if line_index > 0:
            text.append("\n")

        for ch in line:
            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)


def render_moon_startup_art_1() -> None:
    char_style_map = {
        "O": "sun.primary",
        "|": "sun.primary",
        "-": "sun.primary",

        "*": "star.purple",
        "o": "star.blue",
        ".": "star.muted",

        "_": "moon.body",
        "~": "moon.body",
        "`": "moon.body",
        "\\": "moon.body",
        "/": "moon.body",
        "'": "moon.body",
        "\"": "moon.body",
        "(": "moon.body",
        ")": "moon.body",
        "@": "moon.body",

        "U": "nasa.red",
        "S": "nasa.blue",
        "A": "nasa.red",
    }

    lines = MOON_STARTUP_ART_1.splitlines()
    height = len(lines)

    text = Text()

    for row, line in enumerate(lines):
        if row > 0:
            text.append("\n")

        width = len(line)

        for col, ch in enumerate(line):
            # Positional rule for '|'
            if ch == "|":
                left = line[col - 1] if col > 0 else " "
                right = line[col + 1] if col < width - 1 else " "
                above = lines[row - 1][col] if row > 0 and col < len(lines[row - 1]) else " "
                below = lines[row + 1][col] if row < height - 1 and col < len(lines[row + 1]) else " "

                if left == "-" or right == "-" or above == "O" or below == "O":
                    text.append(ch, style="sun.primary")
                else:
                    text.append(ch, style="moon.body")

                continue

            # Normal static mapping
            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)


def render_astronaut_startup_art_1() -> None:
    ground_chars = set("^~'\"")

    lines = ASTRONAUT_STARTUP_ART_1.splitlines()
    total_lines = len(lines)

    # Identify the finial line: the one that contains "<>" (or "< >") near the top
    finial_row = None
    for i, line in enumerate(lines[:6]):  # search only near the top to avoid false matches
        if "<>" in line or "< >" in line:
            finial_row = i
            break

    text = Text()
    flag_stripe_row = 0

    for row, line in enumerate(lines):
        if row > 0:
            text.append("\n")

        pole_start = line.find("||")
        has_flag_cloth = pole_start != -1 and ("=" in line[pole_start:] or ":" in line[pole_start:])

        stripe_style = None
        if has_flag_cloth and "=" in line[pole_start:]:
            stripe_style = "flag.stripe.red" if (flag_stripe_row % 2 == 0) else "flag.stripe.white"
            flag_stripe_row += 1

        is_ground_row = (row == total_lines - 1)
        is_finial_row = (finial_row is not None and row == finial_row)

        for col, ch in enumerate(line):

            # Ground chars should only be "ground" on the ground row;
            # otherwise treat them like astronaut body.
            if ch in ("~", "'", "\""):
                if is_ground_row:
                    text.append(ch, style="ground")
                else:
                    text.append(ch, style="astronaut.body")
                continue

            # < and > are pole-top only on the finial row; otherwise astronaut body
            if ch in ("<", ">"):
                if is_finial_row:
                    text.append(ch, style="pole.top")
                else:
                    text.append(ch, style="astronaut.body")
                continue

            # Ground remaining chars (like ^) on ground row
            if ch in ground_chars:
                text.append(ch, style="ground")
                continue

            # Pole body: only the two columns that make up the '||'
            if ch == "|" and pole_start != -1 and col in (pole_start, pole_start + 1):
                text.append(ch, style="pole.body")
                continue

            if ch == ":" and has_flag_cloth and pole_start != -1 and col > pole_start + 1:
                text.append(ch, style="flag.canton")
                continue

            if ch == "=" and stripe_style and pole_start != -1 and col > pole_start + 1:
                text.append(ch, style=stripe_style)
                continue

            if ch == "U":
                text.append(ch, style="usa.red")
                continue
            if ch == "S":
                text.append(ch, style="usa.blue")
                continue
            if ch == "A":
                text.append(ch, style="usa.red")
                continue

            if ch in "[]*":
                text.append(ch, style="astronaut.detail")
                continue

            if ch.isspace():
                text.append(ch)
            else:
                text.append(ch, style="astronaut.body")

    console.print(text)


def render_astronaut_startup_art_2() -> None:
    highlight_chars = {"=", "*"}

    lines = ASTRONAUT_STARTUP_ART_2.splitlines()
    text = Text()

    for row, line in enumerate(lines):
        if row > 0:
            text.append("\n")

        i = 0
        while i < len(line):
            if line.startswith("NASA", i):
                text.append("N", style="nasa.red")
                text.append("A", style="nasa.blue")
                text.append("S", style="nasa.red")
                text.append("A", style="nasa.blue")
                i += 4
                continue

            ch = line[i]

            if ch.isspace():
                text.append(ch)
            elif ch in highlight_chars:
                text.append(ch, style="astro.metal")
            else:
                text.append(ch, style="astro.body")

            i += 1

    console.print(text)


def render_alien_startup_art_1() -> None:
    char_style_map = {
        "/": "alien.symbol.caret",
        "\\": "alien.symbol.plus",
        "|": "alien.symbol.caret",
        "(": "alien.symbol.plus",
        ")": "alien.symbol.caret",
        "-": "alien.symbol.plus",
        "_": "alien.symbol.caret",

        "!": "alien.symbol.caret",
        "\"": "alien.symbol.plus",
        "'": "alien.symbol.plus",
        "#": "alien.eyes",

        ":": "alien.symbol.caret",
        ".": "alien.symbol.plus",

        "^": "alien.symbol.caret",
        "+": "alien.symbol.plus",
    }

    text = Text()
    for line_index, line in enumerate(ALIEN_STARTUP_ART_1.splitlines()):
        if line_index > 0:
            text.append("\n")

        for ch in line:
            if ch == "A":
                text.append(ch, style="usa.blue")
            elif ch in {"N", "S"}:
                text.append(ch, style="usa.red")
            else:
                style = char_style_map.get(ch)
                text.append(ch, style=style) if style else text.append(ch)

    console.print(text)


def render_alien_startup_art_2() -> None:
    force_astro_body_chars = {"\\", "/"}

    char_style_map = {
        "@": "fire.red",
        "~": "fire.spark",
        "*": "fire.spark",
        ".": "fire.spark",
        "(": "fire.orange",
        ")": "fire.orange",

        "M": "alien.body",
        "O": "alien.body",
        "!": "alien.body",
        "/": "alien.body",
        "\\": "alien.body",
        "-": "alien.body",
        "_": "astro.body",
        "0": "astro.body",
        "%": "alien.body",

        "|": "astro.body",
        "=": "fire.spark",
        "o": "alien.body",
    }

    lines = ALIEN_STARTUP_ART_2.splitlines()
    text = Text()

    for r, line in enumerate(lines):
        if r > 0:
            text.append("\n")

        # Boundary: everything left of the first '@' is "astronaut"
        at_idx = line.find("@")
        astro_side_end = at_idx if at_idx != -1 else len(line)

        for c, ch in enumerate(line):
            if c < astro_side_end and ch in force_astro_body_chars:
                text.append(ch, style="astro.body")
                continue

            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)


def render_satellite_startup_art1() -> None:
    char_style_map = {
        "|": "sat.metal",
        "\\": "sat.metal",
        "/": "sat.metal",
        "_": "sat.metal",
        "-": "sat.metal",
        ":": "sat.metal",
        ";": "sat.metal",
        "L": "sat.metal",

        '"': "sat.light",
        "'": "sat.light",
        "`": "sat.light",
        ".": "sat.light",
        ",": "sat.light",

        "<": "sat.metal",

        "N": "nasa.red",
        "S": "nasa.red",
        "A": "nasa.blue",
    }

    text = Text()
    for line_idx, line in enumerate(SATELLITE_STARTUP_ART_1.splitlines()):
        if line_idx > 0:
            text.append("\n")

        for ch in line:
            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)