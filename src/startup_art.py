from rich.text import Text
from src.utils.console import console
from src.config import *
import random


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


CORE_ONLY = set("ITLH")
RING_ONLY = set("'`")
OVERLAP = set(".,:;+=i)")

SATURN_VARIANTS = [
    "color(172)",   # bronze
    "color(173)",   # darker bronze
    "color(179)",   # warm tan
    "color(99)",    # purple
    "color(99)",    # purple (extra weight)
    "color(98)",    # deeper purple
]
