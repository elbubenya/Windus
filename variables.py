from collections import OrderedDict


def hex_to_ansi(hex_str: str, is_background: bool = False) -> str:
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    
    color_type = "48" if is_background else "38"
    return f"\033[{color_type};2;{r};{g};{b}m"


RESET = "\033[0m"

tile_sheet = {"space": f"{hex_to_ansi('#111111', True)}  {RESET}",
              "window_border": f"{hex_to_ansi('#444444')}██{RESET}",
              "window_border_selected": f"{hex_to_ansi('#777777')}██{RESET}",
              "window_close": f"{hex_to_ansi('#FFFFFF')}{hex_to_ansi('#ff0000', True)}❯❮{RESET}",
              "cursor_0": "[]"}

windows = OrderedDict()
popups = {}

cursor_position = {"y": 1, "x": 1}
last_id = {"value": None}

directions = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}

resolution = {"y": 28, "x": 60}

key_state = {key: False for key in directions}
key_state["shift"] = False