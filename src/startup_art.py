from rich.text import Text
from src.utils.console import console
from src.config import *


def startup_banner1():
    banner = r"""
███╗   ██╗ █████╗ ███████╗ █████╗      █████╗ ██████╗  ██████╗ ██████╗        
████╗  ██║██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗       
██╔██╗ ██║███████║███████╗███████║    ███████║██████╔╝██║   ██║██║  ██║       
██║╚██╗██║██╔══██║╚════██║██╔══██║    ██╔══██║██╔═══╝ ██║   ██║██║  ██║       
██║ ╚████║██║  ██║███████║██║  ██║    ██║  ██║██║     ╚██████╔╝██████╔╝       
╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═════╝        
                                                                              
      ██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗                    
      ██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗                   
      ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝                   
      ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗                   
      ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║                   
      ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝                                                                                                    
        """
    console.print(banner, style="app.banner")


def startup_banner2():
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
    console.print(banner, style="app.banner")


def render_space_startup_art_1() -> None:
    """
    Space Startup Art 1 (Earth)

    - Every visible character = land
    - Only land is colored
    """

    text = Text()

    for line_index, line in enumerate(SPACE_STARTUP_ART_1.splitlines()):
        if line_index > 0:
            text.append("\n")

        for ch in line:
            if ch.isspace():
                # Water → implicit → no styling
                text.append(ch)
            else:
                # Land
                text.append(ch, style="earth.land")

    console.print(text)


def render_spaceship_startup_art_1() -> None:
    char_style_map = {
        # Flame
        "^": "ship.flame.inner",
        "(": "ship.flame.outer",
        ")": "ship.flame.outer",
        ":": "ship.flame.inner",
        ".": "ship.flame.inner",
        "|": "ship.trim",

        # Body
        "/": "ship.trim",
        "\\": "ship.trim",
        "_": "ship.trim",
        "=": "ship.trim",
        "!": "ship.flame.inner",
        "#": "ship.trim",

        # Text
        "U": "ship.usa",
        "S": "ship.usa",
        "A": "ship.usa",
    }

    text = Text()

    for line_index, line in enumerate(SPACESHIP_STARTUP_ART1.splitlines()):
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
        # Structure (white)
        "/": "ship.body",
        "\\": "ship.body",
        "|": "ship.body",
        "-": "ship.body",
        "_": "ship.nasa.blue",
        "!": "ship.nasa.red",

        # Accents
        ".": "ship.dots",
        "(": "ship.paren",
        ")": "ship.paren",

        # NASA letters
        "N": "ship.nasa.red",
        "S": "ship.nasa.red",
        "A": "ship.nasa.blue",
    }

    text = Text()

    for line_index, line in enumerate(SPACESHIP_STARTUP_ART2.splitlines()):
        if line_index > 0:
            text.append("\n")

        for ch in line:
            style = char_style_map.get(ch)
            if style:
                text.append(ch, style=style)
            else:
                text.append(ch)

    console.print(text)