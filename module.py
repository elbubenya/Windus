class Module:
    def __init__(self, pos_y, pos_x, res_y, res_x, borders=False):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.res_y = res_y
        self.res_x = res_x
        self.borders = borders
        self.in_use = False

    @property
    def endpoint_y(self):
        return self.pos_y + self.res_y - 1

    @property
    def endpoint_x(self):
        return self.pos_x + self.res_x - 1

    def activate_use(self):
        self.in_use = True

    def deactivate_use(self):
        self.in_use = False

    def handle_click(self, local_y, local_x):
        self.activate_use()

    def scroll(self, value, window):
        pass

    def go_to_parent(self):
        pass

    def update_hover_selection(self, cursor_position, window):
        pass

    def state_key(self):
        return (self.pos_y, self.pos_x, self.res_y, self.res_x, self.in_use)

    def render(self, grid, window, offset_y=0, offset_x=0):
        raise NotImplementedError

    def _draw(self, grid, window, resolution, local_y, local_x, tile, offset_y=0, offset_x=0):
        """Bounds-checked cell write. A window-border cell is never overwritten,
        so the window's own border always wins over a module's border/content."""
        grid_y = window.pos_y + offset_y + self.pos_y + local_y
        grid_x = window.pos_x + offset_x + self.pos_x + local_x

        if not (0 <= grid_y < resolution["y"] and 0 <= grid_x < resolution["x"]):
            return

        if (grid_y in (window.pos_y, window.endpoint_y) or
                grid_x in (window.pos_x, window.endpoint_x)):
            return

        grid[grid_y][grid_x] = tile
