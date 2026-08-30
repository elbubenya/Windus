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


class TextboxModule(Module, EditableText):
    text_attr = "content"

    def __init__(self, pos_y, pos_x, res_y, res_x, content=None, borders=False, read_only=False):
        Module.__init__(self, pos_y, pos_x, res_y, res_x, borders)
        self.read_only = read_only
        self.content = content if content is not None else "The quick brown fox jumps over a lazy dog."
        self.list_start = 0
        self._init_caret()

    def activate_use(self):
        if self.read_only:
            return

        self.in_use = True
        self.caret = len(self.content)
        text_input["value"] = 1
        suppress_enter["value"] = True

    def deactivate_use(self):
        self.in_use = False
        text_input["value"] = 0

    def _caret_lines(self, max_width):
        lines = []
        paragraphs = self.content.split("\n")

        for p_index, paragraph in enumerate(paragraphs):
            current_line = ""

            for word in paragraph.split(" "):
                while len(word) > max_width:
                    if current_line:
                        lines.append((current_line, 1))
                        current_line = ""
                    lines.append((word[:max_width], 0))
                    word = word[max_width:]

                candidate = f"{current_line} {word}" if current_line else word

                if len(candidate) <= max_width:
                    current_line = candidate
                else:
                    lines.append((current_line, 1))
                    current_line = word

            is_last_paragraph = p_index == len(paragraphs) - 1
            lines.append((current_line, 0 if is_last_paragraph else 1))

        return lines

    def _sync_scroll_to_caret(self, max_width):
        max_rows = self.res_y - 2

        if max_rows <= 0:
            return

        lines = self._caret_lines(max_width) if max_width > 0 else [(self.content, 0)]
        row, _ = self._caret_position(lines)

        if row < self.list_start:
            self.list_start = row
        elif row > self.list_start + max_rows - 1:
            self.list_start = row - max_rows + 1

        max_list_start = max(0, len(lines) - max_rows)
        self.list_start = max(0, min(self.list_start, max_list_start))

    def scroll(self, value, window):
        if self.in_use or not window.selected:
            return

        max_width = (self.res_x - 2) * 2
        max_rows = self.res_y - 2

        if max_width <= 0 or max_rows <= 0:
            return

        line_count = len(self._caret_lines(max_width))
        max_list_start = max(0, line_count - max_rows)

        self.list_start = max(0, min(self.list_start + value, max_list_start))

    def state_key(self):
        return super().state_key() + (self.content, self.caret, self.list_start)

    def render(self, grid, window, offset_y=0, offset_x=0):
        if self.res_y <= 2:
            return

        max_width = (self.res_x - 2) * 2
        max_rows = self.res_y - 2

        if max_width <= 0 or max_rows <= 0:
            return

        caret_row = caret_col = caret_sub = None

        if self.in_use:
            caret_row, caret_char = self.caret_rowcol(max_width)
            caret_row -= self.list_start
            caret_col = caret_char // 2 + 1
            caret_sub = caret_char % 2

            if caret_col > self.res_x - 2:
                caret_row += 1
                caret_col = 1

        lines = self._caret_lines(max_width)
        caret_drawn = False

        for y, (line, _) in enumerate(lines[self.list_start:self.list_start + max_rows], start=1):
            for x, i in enumerate(range(0, len(line), 2), start=1):
                is_caret = y == caret_row and x == caret_col

                if is_caret:
                    caret_drawn = True

                tile = line[i:i + 2].ljust(2)
                tile = _tile_with_caret(tile, caret_sub) if is_caret else f"{hex_to_ansi('#111111', True)}{tile}{RESET}"
                self._draw(grid, window, resolution, y, x, tile, offset_y, offset_x)

        if self.in_use and not caret_drawn and caret_row is not None and 1 <= caret_row <= max_rows:
            self._draw(grid, window, resolution, caret_row, caret_col, _tile_with_caret("  ", caret_sub), offset_y, offset_x)
