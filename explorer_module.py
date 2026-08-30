from module import Module
from path_module import PathModule
from variables import resolution, tile_sheet, hex_to_ansi, RESET


class ExplorerModule(Module):
    def __init__(self, pos_y, pos_x, res_y, res_x, path=".", borders=False):
        super().__init__(pos_y, pos_x, res_y, res_x, borders)
        self.path = PathModule(0, 0, 1, res_x, path=path)
        self.selected_item = None
        self.list_start = 1

    def activate_use(self):
        self.in_use = True

    def handle_click(self, local_y, local_x):
        if self.in_use and local_y == 1:
            self.path.activate_use()
        elif self.in_use and self.open_selected():
            pass
        else:
            self.activate_use()

    def deactivate_use(self):
        if self.path.in_use:
            self.path.deactivate_use()

        self.in_use = False

    def go_to_parent(self):
        self.path.go_to_parent()

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

        self.path.path = file
        self.selected_item = None
        return True

    def scroll(self, value, window):
        if not self.in_use:
            return

        file_count = len(self.files)
        max_rows = self.res_y - 4

        if file_count == 0 or max_rows <= 0:
            return

        # selected_item is an index into the currently visible page (matches render's /
        # update_hover_selection's enumerate(content_listed)), so convert to an absolute
        # file index first.
        current_relative = self.selected_item if self.selected_item is not None else 0
        absolute = (self.list_start - 1) + current_relative
        absolute = max(0, min(file_count - 1, absolute + value))

        visible_start = self.list_start - 1
        visible_end = visible_start + max_rows - 1

        if absolute < visible_start:
            self.list_start = absolute + 1
        elif absolute > visible_end:
            self.list_start = absolute - max_rows + 2

        max_list_start = max(1, file_count - max_rows + 1)
        self.list_start = max(1, min(self.list_start, max_list_start))

        self.selected_item = absolute - (self.list_start - 1)

    def update_hover_selection(self, cursor_position, window):
        self.selected_item = None

        for item_index, (content_y, _, _) in enumerate(self.content_listed):
            grid_y = window.pos_y + self.pos_y + content_y + 2

            if (cursor_position["y"] == grid_y and
                    window.pos_x + self.pos_x < cursor_position["x"] < window.pos_x + self.endpoint_x):
                self.selected_item = item_index
                break

    @property
    def files(self):
        try:
            entries = list(self.path.path.iterdir())
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

    def state_key(self):
        return super().state_key() + (self.selected_item, self.list_start, self.path.state_key())

    def render(self, grid, window, offset_y=0, offset_x=0):
        self.path.res_x = self.res_x
        self.path.render(grid, window, offset_y + self.pos_y, offset_x + self.pos_x)

        max_width = (self.res_x - 2) * 2

        # Separator
        separator_local_y = 2

        for local_x in range(1, self.res_x - 1):
            tile = (
                f"{hex_to_ansi('#777777')}{hex_to_ansi('#111111', True)}▔▔{RESET}"
                if window.selected else
                f"{hex_to_ansi('#444444')}{hex_to_ansi('#111111', True)}▔▔{RESET}"
            )
            self._draw(grid, window, resolution, separator_local_y, local_x, tile, offset_y, offset_x)

        # Files / folders
        for item_index, (content_y, file, name) in enumerate(self.content_listed):
            if file.is_dir():
                name = tile_sheet["folder"] + name
            elif file.is_file():
                name = tile_sheet["file"] + name

            name = name[:max_width]
            selected = item_index == self.selected_item

            for content_x, i in enumerate(range(0, len(name), 2), start=1):
                tile = name[i:i + 2].ljust(2)

                if selected and self.in_use:
                    tile = f"{hex_to_ansi('#000000')}{hex_to_ansi('#FFFFFF', True)}{tile}{RESET}"
                else:
                    tile = f"{hex_to_ansi('#111111', True)}{tile}{RESET}"

                self._draw(grid, window, resolution, content_y + 2, content_x, tile, offset_y, offset_x)
