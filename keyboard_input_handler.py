from queue import SimpleQueue
from pynput import keyboard

from variables import windows, text_input, suppress_enter


_pending_keys = SimpleQueue()

_ARROW_DIRECTIONS = {
    keyboard.Key.up: (-1, 0),
    keyboard.Key.down: (1, 0),
    keyboard.Key.left: (0, -1),
    keyboard.Key.right: (0, 1),
}


class EditableText:
    """Mixin giving a window a movable caret over one of its own string attributes."""

    text_attr = "content"

    def _init_caret(self):
        self.caret = len(self._text)

    @property
    def _text(self):
        return getattr(self, self.text_attr)

    @_text.setter
    def _text(self, value):
        setattr(self, self.text_attr, value)

    def _caret_lines(self, max_width):
        """Returns [(line_text, consumed_after)]: consumed_after is how many original
        characters were swallowed between this line and the next (a wrapped space,
        a newline, or 0 for a hard mid-word split / the last line)."""
        return [(self._text, 0)]

    @staticmethod
    def _line_offset(lines, row):
        return sum(len(line) + consumed for line, consumed in lines[:row])

    def _caret_position(self, lines):
        offset = 0

        for row, (line, consumed) in enumerate(lines):
            line_len = len(line) + consumed

            if self.caret < offset + line_len or row == len(lines) - 1:
                col = max(0, min(len(line), self.caret - offset))
                return row, col

            offset += line_len

        return 0, 0

    def move_caret(self, dy, dx, max_width):
        lines = self._caret_lines(max_width) if max_width > 0 else [(self._text, 0)]

        if dx:
            self.caret = max(0, min(len(self._text), self.caret + dx))
            return

        if dy and lines:
            row, col = self._caret_position(lines)
            target_row = max(0, min(len(lines) - 1, row + dy))
            target_col = min(col, len(lines[target_row][0]))
            self.caret = max(0, min(len(self._text), self._line_offset(lines, target_row) + target_col))

    def caret_rowcol(self, max_width):
        """Returns (content_y, char_col): content_y matches content_listed's row,
        char_col is the 0-based character offset within that row (not a tile index)."""
        lines = self._caret_lines(max_width) if max_width > 0 else [(self._text, 0)]
        row, col = self._caret_position(lines)
        return row + 1, col

    def insert_char(self, char):
        text = self._text
        self._text = text[:self.caret] + char + text[self.caret:]
        self.caret += len(char)

    def backspace(self):
        if self.caret > 0:
            text = self._text
            self._text = text[:self.caret - 1] + text[self.caret:]
            self.caret -= 1


def _on_press(key):
    if key == keyboard.Key.enter and suppress_enter["value"]:
        suppress_enter["value"] = False
        return

    if text_input["value"]:
        _pending_keys.put(key)


_listener = keyboard.Listener(on_press=_on_press)
_listener.start()


def _active_text_window():
    for window in windows.values():
        if getattr(window, "in_use", False) and isinstance(window, EditableText):
            return window
    return None


def handle_text_input():
    window = _active_text_window()

    while not _pending_keys.empty():
        key = _pending_keys.get()

        if window is None:
            continue

        max_width = (window.res_x - 2) * 2

        if key == keyboard.Key.backspace:
            window.backspace()
        elif key == keyboard.Key.space:
            window.insert_char(" ")
        elif key == keyboard.Key.enter:
            if text_input["value"] == 2:
                if hasattr(window, "deactivate_use"):
                    window.deactivate_use()
                window.selected = False
                text_input["value"] = 0
            else:
                window.insert_char("\n")
        elif key in _ARROW_DIRECTIONS:
            dy, dx = _ARROW_DIRECTIONS[key]
            window.move_caret(dy, dx, max_width)
        elif isinstance(key, keyboard.KeyCode) and key.char is not None:
            window.insert_char(key.char)
