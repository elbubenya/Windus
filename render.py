import sys

from variables import windows, popups, cursor_position, resolution, tile_sheet, window_used, text_input, last_id, hex_to_ansi, RESET
from cursor import overlapped_window_id, overlapped_popup_button


def truncate_with_dots(text, max_width, keep_start=False):
    if len(text) <= max_width:
        return text
    if max_width <= 3:
        return "." * max_width
    if keep_start:
        return text[:max_width - 3] + "..."
    return "..." + text[-(max_width - 3):]


def prerender_window_title(grid, window, window_id):
    max_width = (window.res_x - 2) * 2

    if max_width <= 0:
        return

    list_start = getattr(window.module, "list_start", None)
    title = str(window_id) if list_start is None else f"{window_id} {list_start}"
    title = truncate_with_dots(title, max_width, keep_start=True)

    if len(title) == max_width and max_width >= 2:
        title = truncate_with_dots(str(window_id), max_width - 2, keep_start=True)

    highlighted = window.selected or getattr(window.module, "in_use", False)
    bg = "#777777" if highlighted else "#444444"

    for x, i in enumerate(range(0, len(title), 2), start=1):
        grid_y = window.pos_y
        grid_x = window.pos_x + x

        if (0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            grid[grid_y][grid_x] = (
                f"{hex_to_ansi('#FFFFFF')}"
                f"{hex_to_ansi(bg, True)}"
                f"{title[i:i+2].ljust(2)}"
                f"{RESET}"
            )


def prerender_windows(grid):
    for window_id, window in reversed(windows.items()):
        highlighted = window.selected or getattr(window.module, "in_use", False)

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
                    grid[y][x] = tile_sheet["window_border_selected"] if highlighted else tile_sheet["window_border"]
                else:
                    grid[y][x] = tile_sheet["space"]

        prerender_window_title(grid, window, window_id)

        if window.module is not None:
            window.module.render(grid, window)


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

    if not window_used["value"] and not text_input["value"]:
        grid[cursor_position["y"]][cursor_position["x"]] = tile_sheet["cursor_0"]
    return grid


_last_snapshot = None


def _snapshot():
    return (
        (cursor_position["y"], cursor_position["x"]),
        tuple((wid, w.pos_y, w.pos_x, w.res_y, w.res_x, w.selected,
               w.module.state_key() if w.module is not None else None)
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
    sys.stdout.write(f"\n{overlapped_window_id()} | {last_id['value']}                                        ")
    sys.stdout.write(f"\n{overlapped_popup_button()}                                        ")
    sys.stdout.flush()
