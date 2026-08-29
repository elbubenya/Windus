import sys

from txt_window import TextWindow
from explorer_window import ExplorerWindow
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

    title = truncate_with_dots(str(window_id), max_width, keep_start=True)

    if len(title) == max_width and max_width >= 2:
        title = truncate_with_dots(str(window_id), max_width - 2, keep_start=True)

    bg = "#777777" if window.selected else "#444444"

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

def _tile_with_caret(tile, caret_sub):
    chars = []

    for i, char in enumerate(tile):
        if i == caret_sub:
            chars.append(f"{hex_to_ansi('#000000')}{hex_to_ansi('#FFFFFF', True)}{char}{RESET}")
        else:
            chars.append(f"{hex_to_ansi('#111111', True)}{char}{RESET}")

    return "".join(chars)


def prerender_txt_content(grid, window):
    caret_row = caret_col = caret_sub = None

    if window.in_use:
        caret_row, caret_char = window.caret_rowcol((window.res_x - 2) * 2)
        caret_col = caret_char // 2 + 1
        caret_sub = caret_char % 2

    caret_drawn = False

    for (content_y, content_x), tile in window.content_listed:
        grid_y = window.pos_y + content_y
        grid_x = window.pos_x + content_x

        is_caret = content_y == caret_row and content_x == caret_col

        if is_caret:
            caret_drawn = True

        if (0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            if is_caret:
                grid[grid_y][grid_x] = _tile_with_caret(tile, caret_sub)
            else:
                grid[grid_y][grid_x] = f"{hex_to_ansi('#111111', True)}{tile}{RESET}"

    max_rows = window.res_y - 2

    if window.in_use and not caret_drawn and 1 <= caret_row <= max_rows:
        grid_y = window.pos_y + caret_row
        grid_x = window.pos_x + caret_col

        if (window.pos_y < grid_y < window.endpoint_y and
            window.pos_x < grid_x < window.endpoint_x and
            0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            grid[grid_y][grid_x] = _tile_with_caret("  ", caret_sub)


def _scrolled_to_caret(text, caret, max_width):
    """Slides a max_width-wide, "..."-prefixed window over text so caret always stays visible."""
    if len(text) <= max_width:
        return text, caret

    if max_width <= 3:
        return "." * max_width, None

    room = max_width - 3
    start = max(0, min(caret - room, len(text) - room))

    return "..." + text[start:start + room], 3 + (caret - start)


def prerender_explorer_content(grid, window):
    max_width = (window.res_x - 2) * 2 - 1
    editing = getattr(window, "editing_path", False)

    if editing:
        path, caret_char = _scrolled_to_caret(window.path_input, window.caret, max_width)
    else:
        path = truncate_with_dots(str(window.path), max_width)
        caret_char = None

    caret_col = caret_char // 2 + 1 if caret_char is not None else None
    caret_sub = caret_char % 2 if caret_char is not None else None
    caret_drawn = False

    for x, i in enumerate(range(0, len(path), 2), start=1):
        grid_y = window.pos_y + 1
        grid_x = window.pos_x + x

        is_caret = editing and x == caret_col

        if is_caret:
            caret_drawn = True

        if (window.pos_y < grid_y < window.endpoint_y and
            window.pos_x < grid_x < window.endpoint_x and
            0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            tile = path[i:i+2].ljust(2)

            if is_caret:
                grid[grid_y][grid_x] = _tile_with_caret(tile, caret_sub)
            else:
                grid[grid_y][grid_x] = f"{hex_to_ansi('#111111', True)}{tile}{RESET}"

    if editing and not caret_drawn and caret_col is not None:
        grid_y = window.pos_y + 1
        grid_x = window.pos_x + caret_col

        if (window.pos_y < grid_y < window.endpoint_y and
            window.pos_x < grid_x < window.endpoint_x and
            0 <= grid_y < resolution["y"] and
            0 <= grid_x < resolution["x"]):
            grid[grid_y][grid_x] = _tile_with_caret("  ", caret_sub)

    # Separator
    separator_y = window.pos_y + 2

    for x in range(window.pos_x + 1, window.endpoint_x):
        if 0 <= separator_y < resolution["y"] and 0 <= x < resolution["x"]:
            grid[separator_y][x] = (
                f"{hex_to_ansi('#777777')}"
                f"{hex_to_ansi('#111111', True)}"
                f"▔▔"
                f"{RESET}"
            ) if window.selected else (
                f"{hex_to_ansi('#444444')}"
                f"{hex_to_ansi('#111111', True)}"
                f"▔▔"
                f"{RESET}"
            )

    # Files / folders
    for item_index, (content_y, file, name) in enumerate(window.content_listed):

        if file.is_dir():
            name = tile_sheet["folder"] + name
        elif file.is_file():
            name = tile_sheet["file"] + name

        name = name[:max_width]

        selected = item_index == window.selected_item

        for content_x, i in enumerate(range(0, len(name), 2), start=1):
            grid_y = window.pos_y + content_y + 2
            grid_x = window.pos_x + content_x

            if (0 <= grid_y < resolution["y"] and
                0 <= grid_x < resolution["x"]):

                tile = name[i:i+2].ljust(2)

                if selected and window.in_use:
                    grid[grid_y][grid_x] = (
                        f"{hex_to_ansi('#000000')}"
                        f"{hex_to_ansi('#FFFFFF', True)}"
                        f"{tile}"
                        f"{RESET}"
                    )
                else:
                    grid[grid_y][grid_x] = (
                        f"{hex_to_ansi('#111111', True)}"
                        f"{tile}"
                        f"{RESET}"
                    )


def prerender_windows(grid):
    for window_id, window in reversed(windows.items()):
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

        prerender_window_title(grid, window, window_id)

        if isinstance(window, TextWindow):
            prerender_txt_content(grid, window)

        if isinstance(window, ExplorerWindow):
            prerender_explorer_content(grid, window)


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
               getattr(w, "in_use", False),
               getattr(w, "editing_path", False),
               getattr(w, "content", None),
               getattr(w, "path", None),
               getattr(w, "path_input", None),
               getattr(w, "selected_item", None),
               getattr(w, "caret", None))
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