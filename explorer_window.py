from pathlib import Path

from window import Window
from keyboard_input_handler import EditableText
from variables import text_input, suppress_enter


class ExplorerWindow(Window, EditableText):
    text_attr = "path_input"

    def __init__(self, pos_y, pos_x, res_y, res_x, path):
        super().__init__(pos_y, pos_x, res_y, res_x)
        self.path = Path(path)
        self.path_input = str(self.path)
        self.selected_item = None
        self.in_use = False
        self.editing_path = False
        self._init_caret()
        self.list_start = 1

    def activate_use(self):
        self.selected = True
        self.in_use = True

    def open_selected(self):
        if self.selected_item is None:
            return False

        files = self.files
        absolute = (self.list_start - 1) + self.selected_item

        self.list_start = 1

        if absolute >= len(files):
            return False

        file = files[absolute]

        if not file.is_dir():
            return False

        self.path = file
        self.selected_item = None
        return True

    def activate_path_edit(self):
        self.selected = True
        self.in_use = True
        self.editing_path = True
        self.path_input = str(self.path)
        self.caret = len(self.path_input)
        text_input["value"] = 2
        suppress_enter["value"] = True

    def deactivate_use(self):
        self.in_use = False

        if not self.editing_path:
            return

        self.editing_path = False
        text_input["value"] = 0

        candidate = Path(self.path_input)

        if candidate.is_dir():
            self.path = candidate
            self.list_start = 1
            self.selected_item = None
        else:
            self.path_input = str(self.path)

    @property
    def files(self):
        try:
            entries = list(self.path.iterdir())
        except OSError:
            return []

        return sorted(
            entries,
            key=lambda file: (not file.is_dir(), file.name.lower())
        )

    @property
    def content_listed(self):
        content_listed = []

        if self.res_y <= 4:
            return content_listed

        max_width = (self.res_x - 2) * 2
        max_rows = self.res_y - 4

        if max_width <= 0 or max_rows <= 0:
            return content_listed

        for y, file in enumerate(
            self.files[self.list_start - 1:self.list_start - 1 + max_rows],
            start=self.list_start
        ):
            name = file.name[:max_width]

            content_listed.append((
                y - self.list_start + 1,
                file,
                name
            ))

        return content_listed

def get_path_parent(window):
    if isinstance(window, ExplorerWindow) and window.path.parent != window.path and window.in_use:
        window.path = window.path.parent

def scroll(window, value):
    if not (isinstance(window, ExplorerWindow) and window.in_use):
        return

    file_count = len(window.files)
    max_rows = window.res_y - 4

    if file_count == 0 or max_rows <= 0:
        return

    # selected_item is an index into the currently visible page (matches render.py /
    # cursor.py's enumerate(content_listed)), so convert to an absolute file index first.
    current_relative = window.selected_item if window.selected_item is not None else 0
    absolute = (window.list_start - 1) + current_relative
    absolute = max(0, min(file_count - 1, absolute + value))

    visible_start = window.list_start - 1
    visible_end = visible_start + max_rows - 1

    if absolute < visible_start:
        window.list_start = absolute + 1
    elif absolute > visible_end:
        window.list_start = absolute - max_rows + 2

    max_list_start = max(1, file_count - max_rows + 1)
    window.list_start = max(1, min(window.list_start, max_list_start))

    window.selected_item = absolute - (window.list_start - 1)
