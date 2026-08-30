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
        elif dy and lines:
            row, col = self._caret_position(lines)
            target_row = max(0, min(len(lines) - 1, row + dy))
            target_col = min(col, len(lines[target_row][0]))
            self.caret = max(0, min(len(self._text), self._line_offset(lines, target_row) + target_col))

        self._sync_scroll_to_caret(max_width)

    def _sync_scroll_to_caret(self, max_width):
        """Hook for subclasses that scroll their own viewport (e.g. TextboxModule.list_start)."""

    def caret_rowcol(self, max_width):
        lines = self._caret_lines(max_width) if max_width > 0 else [(self._text, 0)]
        row, col = self._caret_position(lines)
        return row + 1, col

    def insert_char(self, char, max_width=None):
        text = self._text
        self._text = text[:self.caret] + char + text[self.caret:]
        self.caret += len(char)

        if max_width is not None:
            self._sync_scroll_to_caret(max_width)

    def backspace(self, max_width=None):
        if self.caret > 0:
            text = self._text
            self._text = text[:self.caret - 1] + text[self.caret:]
            self.caret -= 1

        if max_width is not None:
            self._sync_scroll_to_caret(max_width)


def _on_press(key):
    if key == keyboard.Key.enter and suppress_enter["value"]:
        suppress_enter["value"] = False
        return

    if text_input["value"]:
        _pending_keys.put(key)


_listener = keyboard.Listener(on_press=_on_press)
_listener.start()


def _active_text_module():
    for window in windows.values():
        module = window.module

        if module is None:
            continue

        candidates = (module, getattr(module, "path", None))

        for candidate in candidates:
            if isinstance(candidate, EditableText) and candidate.in_use:
                return window, candidate

    return None, None


def handle_text_input():
    window, module = _active_text_module()

    while not _pending_keys.empty():
        key = _pending_keys.get()

        if module is None:
            continue

        max_width = (module.res_x - 2) * 2

        if key == keyboard.Key.backspace:
            module.backspace(max_width)
        elif key == keyboard.Key.space:
            module.insert_char(" ", max_width)
        elif key == keyboard.Key.enter:
            if text_input["value"] == 2:
                module.deactivate_use()
                window.selected = False
                text_input["value"] = 0
            else:
                module.insert_char("\n", max_width)
        elif key in _ARROW_DIRECTIONS:
            dy, dx = _ARROW_DIRECTIONS[key]
            module.move_caret(dy, dx, max_width)
        elif isinstance(key, keyboard.KeyCode) and key.char is not None:
            module.insert_char(key.char, max_width)
