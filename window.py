from variables import windows, directions, resolution, cursor_position


class Window:
    def __init__(self, pos_y, pos_x, res_y, res_x):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.res_y = res_y
        self.res_x = res_x
        self.selected = 0

    @property
    def endpoint_y(self):
        return self.pos_y + self.res_y - 1

    @property
    def endpoint_x(self):
        return self.pos_x + self.res_x - 1

    def move_window(self, dy, dx):
        if self.selected:
            self.pos_y += dy
            self.pos_x += dx

    def scale_window(self, pressed):
        if self.selected:
            for key, (dy, dx) in directions.items():
                if pressed[key]:
                    self.res_y += dy
                    self.res_x += dx

        self.res_y = max(self.res_y,  2)
        self.res_x = max(self.res_x, 3)

        if self.selected:
            cursor_position["y"] = max(cursor_position["y"], self.pos_y)
            cursor_position["x"] = max(cursor_position["x"], self.pos_x)


class TextWindow(Window):
    def __init__(self, pos_y, pos_x, res_y, res_x):
        super().__init__(pos_y, pos_x, res_y, res_x)
        self.content = "The quick brown fox jumps over a lazy dog."

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


def new_window(pos_y, pos_x, window_class):
    new_id = max(windows, default=-1) + 1
    windows[new_id] = window_class(pos_y, pos_x, 5, 5)
    windows.move_to_end(new_id, last=False)


def delete_window(id):
    windows.pop(id)
