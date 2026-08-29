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

    def activate_use(self):
        self.selected = True
        self.in_use = True

    def open_selected(self):
        if self.selected_item is None:
            return False

        files = self.files

        if self.selected_item >= len(files):
            return False

        file = files[self.selected_item]

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
            self.selected_item = None
        else:
            self.path_input = str(self.path)

    @property
    def files(self):
        return sorted(
            self.path.iterdir(),
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

        for y, file in enumerate(self.files[:max_rows], start=1):
            name = file.name[:max_width]

            content_listed.append((
                y,
                file,
                name
            ))

        return content_listed

def path_back(window):
    if isinstance(window, ExplorerWindow) and window.path.parent != window.path and window.in_use:
        window.path = window.path.parent
