from pathlib import Path

from module import Module
from text_input_handler import EditableText
from variables import text_input, suppress_enter, resolution, hex_to_ansi, RESET


def _tile_with_caret(tile, caret_sub):
    chars = []

    for i, char in enumerate(tile):
        if i == caret_sub:
            chars.append(f"{hex_to_ansi('#000000')}{hex_to_ansi('#FFFFFF', True)}{char}{RESET}")
        else:
            chars.append(f"{hex_to_ansi('#111111', True)}{char}{RESET}")

    return "".join(chars)


def truncate_with_dots(text, max_width, keep_start=False):
    if len(text) <= max_width:
        return text
    if max_width <= 3:
        return "." * max_width
    if keep_start:
        return text[:max_width - 3] + "..."
    return "..." + text[-(max_width - 3):]


def _scrolled_to_caret(text, caret, max_width):
    if len(text) <= max_width:
        return text, caret

    if max_width <= 3:
        return "." * max_width, None

    room = max_width - 3
    start = max(0, min(caret - room, len(text) - room))

    return "..." + text[start:start + room], 3 + (caret - start)


class PathModule(Module, EditableText):
    text_attr = "path_input"

    def __init__(self, pos_y, pos_x, res_y, res_x, path=".", borders=False):
        Module.__init__(self, pos_y, pos_x, res_y, res_x, borders)
        self.path = Path(path)
        self.path_input = str(self.path)
        self._init_caret()

    def activate_use(self):
        self.in_use = True
        self.path_input = str(self.path)
        self.caret = len(self.path_input)
        text_input["value"] = 2
        suppress_enter["value"] = True

    def deactivate_use(self):
        self.in_use = False

        if text_input["value"] == 2:
            text_input["value"] = 0

        candidate = Path(self.path_input)

        if candidate.is_dir():
            self.path = candidate
        else:
            self.path_input = str(self.path)

    def go_to_parent(self):
        if self.path.parent != self.path:
            self.path = self.path.parent

    def state_key(self):
        return super().state_key() + (str(self.path), self.path_input, self.caret)

    def render(self, grid, window, offset_y=0, offset_x=0):
        max_width = (self.res_x - 2) * 2 - 1

        if self.in_use:
            path, caret_char = _scrolled_to_caret(self.path_input, self.caret, max_width)
        else:
            path = truncate_with_dots(str(self.path), max_width)
            caret_char = None

        caret_col = caret_char // 2 + 1 if caret_char is not None else None
        caret_sub = caret_char % 2 if caret_char is not None else None
        caret_drawn = False

        for x, i in enumerate(range(0, len(path), 2), start=1):
            is_caret = self.in_use and x == caret_col

            if is_caret:
                caret_drawn = True

            tile = path[i:i + 2].ljust(2)
            tile = _tile_with_caret(tile, caret_sub) if is_caret else f"{hex_to_ansi('#111111', True)}{tile}{RESET}"
            self._draw(grid, window, resolution, 1, x, tile, offset_y, offset_x)

        if self.in_use and not caret_drawn and caret_col is not None:
            self._draw(grid, window, resolution, 1, caret_col, _tile_with_caret("  ", caret_sub), offset_y, offset_x)
