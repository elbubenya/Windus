from window import Window
from keyboard_input_handler import EditableText
from variables import text_input, suppress_enter


class TextWindow(Window, EditableText):
    text_attr = "content"

    def __init__(self, pos_y, pos_x, res_y, res_x, path=None):
        super().__init__(pos_y, pos_x, res_y, res_x)
        self.path = path
        self.in_use = False
        if self.path is None:
            self.content = "The quick brown fox jumps over a lazy dog."
        else:
            self.content = "Wow, this txt has a path!"
        self._init_caret()
        self.list_start = 0

    def activate_use(self):
        self.selected = True
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

    @property
    def content_listed(self):
        content_listed = []

        if self.res_y <= 2:
            return content_listed

        max_width = (self.res_x - 2) * 2
        max_rows = self.res_y - 2

        if max_width <= 0 or max_rows <= 0:
            return content_listed

        lines = self._caret_lines(max_width)

        for y, (line, _) in enumerate(lines[self.list_start:self.list_start + max_rows], start=1):
            for x, i in enumerate(range(0, len(line), 2), start=1):
                content_listed.append((
                    (y, x),
                    line[i:i+2].ljust(2)
                ))

        return content_listed


def scroll(window, value):
    if not (isinstance(window, TextWindow) and window.selected):
        return

    max_width = (window.res_x - 2) * 2
    max_rows = window.res_y - 2

    if max_width <= 0 or max_rows <= 0:
        return

    line_count = len(window._caret_lines(max_width))
    max_list_start = max(0, line_count - max_rows)

    window.list_start = max(0, min(window.list_start + value, max_list_start))
