import sys
from window import TextWindow
from variables import windows, popups, cursor_position, resolution, tile_sheet, hex_to_ansi, RESET
from cursor import overlapped_window_id, overlapped_popup_button, get_last_id


def prerender_txt_content(grid, window):
    for (content_y, content_x), tile in window.content_listed:
        grid_y = window.pos_y + content_y
        grid_x = window.pos_x + content_x

        if (0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            grid[grid_y][grid_x] = f"{hex_to_ansi('#111111', True)}{tile}{RESET}"


def prerender_windows(grid):
    for window in reversed(windows.values()):
        for y in range(window.pos_y, window.endpoint_y + 1):
            for x in range(window.pos_x, window.endpoint_x + 1):

                if not (0 <= y < resolution["y"] and
                        0 <= x < resolution["x"]):
                    continue

                if y == window.pos_y and x == window.endpoint_x:
                    grid[y][x] = tile_sheet["window_close"]
                elif (y == window.pos_y or
                    x == window.pos_x or
                    y == window.endpoint_y or
                    x == window.endpoint_x):
                    grid[y][x] = tile_sheet["window_border_selected"] if window.selected else tile_sheet["window_border"]
                else:
                    grid[y][x] = tile_sheet["space"]

        if isinstance(window, TextWindow):
            prerender_txt_content(grid, window)


def prerender_popups(grid):
    for popup in reversed(popups.values()):
        for y in range(popup.res_y):
            for x in range(popup.res_x):

                grid_y = popup.pos_y + y
                grid_x = popup.pos_x + x

                if not (0 <= grid_y < resolution["y"] and
                        0 <= grid_x < resolution["x"]):
                    continue

                if y < len(popup.content_listed):
                    row = popup.content_listed[y]
                else:
                    row = []

                if x < len(row):
                    tile = row[x]
                elif (grid_y == cursor_position["y"] and
                      popup.pos_x <= cursor_position["x"] < popup.pos_x + popup.res_x):
                    tile = f"{hex_to_ansi('#FFFFFF', True)}  {RESET}"
                else:
                    tile = f"{hex_to_ansi('#666666', True)}  {RESET}"

                if (grid_y == cursor_position["y"] and
                    popup.pos_x <= cursor_position["x"] < popup.pos_x + popup.res_x):
                    grid[grid_y][grid_x] = (
                        hex_to_ansi("#000000") + hex_to_ansi("#FFFFFF", is_background=True) + tile + "\033[0m"
                    )
                else:
                    grid[grid_y][grid_x] = (
                        hex_to_ansi("#666666", is_background=True) + tile + "\033[0m"
                    )


def prerender():
    grid = [["  " for _ in range(resolution["x"])]
            for _ in range(resolution["y"])]

    prerender_windows(grid)
    prerender_popups(grid)

    grid[cursor_position["y"]][cursor_position["x"]] = tile_sheet["cursor_0"]
    return grid


_last_snapshot = None


def _snapshot():
    return (
        (cursor_position["y"], cursor_position["x"]),
        tuple((wid, w.pos_y, w.pos_x, w.res_y, w.res_x, w.selected)
              for wid, w in windows.items()),
        tuple((pid, id(popup)) for pid, popup in popups.items()),
    )


def render():
    global _last_snapshot

    current_snapshot = _snapshot()
    if current_snapshot == _last_snapshot:
        return
    _last_snapshot = current_snapshot

    grid = prerender()

    sys.stdout.write("\033[H")
    sys.stdout.write("\n".join("".join(row) for row in grid))
    sys.stdout.write(f"\n{overlapped_window_id()} + {get_last_id()}                    ")
    sys.stdout.write(f"\n{overlapped_popup_button()}                    ")
    sys.stdout.flush()