import re

from variables import windows, directions, cursor_position


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


def reset_windows():
    for window in windows.values():
        window.selected = False
        if hasattr(window, "deactivate_use"):
            window.deactivate_use()


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
