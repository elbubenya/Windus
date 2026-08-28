import re
from pathlib import Path

from variables import windows, directions, resolution, cursor_position, window_used


class Window:
    def __init__(self, pos_y, pos_x, res_y, res_x):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.res_y = res_y
        self.res_x = res_x
        self.selected = False

    @property
    def endpoint_y(self):
        return self.pos_y + self.res_y - 1

    @property
    def endpoint_x(self):
        return self.pos_x + self.res_x - 1

    def move_window(self, dy, dx):
        if self.selected and not getattr(self, "in_use", False):
            self.pos_y += dy
            self.pos_x += dx

    def scale_window(self, pressed):
        movable = self.selected and not getattr(self, "in_use", False)

        if movable:
            for key, (dy, dx) in directions.items():
                if pressed[key]:
                    self.res_y += dy
                    self.res_x += dx

        self.res_y = max(self.res_y,  2)
        self.res_x = max(self.res_x, 3)

        if movable:
            cursor_position["y"] = max(cursor_position["y"], self.pos_y)
            cursor_position["x"] = max(cursor_position["x"], self.pos_x)


class TextWindow(Window):
    def __init__(self, pos_y, pos_x, res_y, res_x, path=None):
        super().__init__(pos_y, pos_x, res_y, res_x)
        self.path = path
        self.in_use = False
        if self.path is None:
            self.content = "The quick brown fox jumps over a lazy dog."
        else:
            self.content = "Wow, this txt has a path!"

    def activate_use(self):
        self.selected = True
        self.in_use = True
        window_used["value"] = True

    def deactivate_use(self):
        self.in_use = False
        window_used["value"] = False

    @property
    def content_listed(self):
        content_listed = []

        if self.res_y <= 2:
            return content_listed

        max_width = (self.res_x - 2) * 2
        max_rows = self.res_y - 2

        if max_width <= 0 or max_rows <= 0:
            return content_listed

        lines = []
        current_line = ""

        for word in self.content.split(" "):
            while len(word) > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append(word[:max_width])
                word = word[max_width:]

            candidate = f"{current_line} {word}" if current_line else word

            if len(candidate) <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for y, line in enumerate(lines[:max_rows], start=1):
            for x, i in enumerate(range(0, len(line), 2), start=1):
                content_listed.append((
                    (y, x),
                    line[i:i+2].ljust(2)
                ))

        return content_listed


class ExplorerWindow(Window):
    def __init__(self, pos_y, pos_x, res_y, res_x, path):
        super().__init__(pos_y, pos_x, res_y, res_x)
        self.path = Path(path)
        self.selected_item = None
        self.in_use = False

    def activate_use(self):
        self.selected = True
        self.in_use = True

    def deactivate_use(self):
        self.in_use = False

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


def new_window(pos_y, pos_x, window_class, *args):
    prefix = re.sub(r'(?<!^)(?=[A-Z])', ' ', window_class.__name__)

    ids = [
        int(id.removeprefix(prefix))
        for id in windows
        if id.startswith(prefix)
    ]

    new_id = f"{prefix} {max(ids, default=-1) + 1}"

    windows[new_id] = window_class(
        pos_y,
        pos_x,
        5,
        5,
        *args
    )

    windows.move_to_end(new_id, last=False)


def delete_window(id):
    windows.pop(id)
