from variables import windows, popups, cursor_position, last_id, directions, resolution
from explorer_window import ExplorerWindow


def update_explorer_selection():
    for window in windows.values():
        if not isinstance(window, ExplorerWindow):
            continue

        window.selected_item = None

        for item_index, (content_y, _, _) in enumerate(window.content_listed):
            grid_y = window.pos_y + content_y + 2

            if (cursor_position["y"] == grid_y and
                    window.pos_x < cursor_position["x"] < window.endpoint_x):
                window.selected_item = item_index
                break


def cursor_move(pressed):
    old_y, old_x = cursor_position["y"], cursor_position["x"]

    for key, (dy, dx) in directions.items():
        if pressed[key]:
            cursor_position["y"] += dy
            cursor_position["x"] += dx

    cursor_position["y"] = min(max(cursor_position["y"], 0), resolution["y"]-1)
    cursor_position["x"] = min(max(cursor_position["x"], 0), resolution["x"]-1)

    update_explorer_selection()

    return cursor_position["y"] - old_y, cursor_position["x"] - old_x


def overlapped_window_id():
    for id, window in windows.items():
        if (window.pos_y <= cursor_position["y"] <= window.endpoint_y and
                window.pos_x <= cursor_position["x"] <= window.endpoint_x):
            if not popups:
                last_id["value"] = id
            close_state = (window.pos_y == cursor_position["y"] and
                           window.endpoint_x == cursor_position["x"])
            return id, close_state
    return None


def overlapped_popup_button():
    for popup in popups.values():
        for y, button in enumerate(popup.content):
            if (popup.pos_y + y == cursor_position["y"] and
                    popup.pos_x <= cursor_position["x"] < popup.pos_x + popup.res_x):
                return button
    return None


def cursor_select(ignore_popups=False, use=False):
    if last_id["value"] is None or (overlapped_popup_button() is not None and not ignore_popups):
        return

    id = last_id["value"]
    window = windows[id]

    if use:
        if hasattr(window, "activate_use"):
            window.activate_use()
    elif ignore_popups:
        window.selected = True
    else:
        on_border = (cursor_position["y"] == window.pos_y or
                     cursor_position["x"] == window.pos_x or
                     cursor_position["y"] == window.endpoint_y or
                     cursor_position["x"] == window.endpoint_x)

        if on_border:
            if hasattr(window, "activate_use") and window.in_use:
                window.deactivate_use()
                window.selected = False
            else:
                window.selected = not window.selected
        elif not hasattr(window, "activate_use"):
            window.selected = not window.selected
        elif isinstance(window, ExplorerWindow) and cursor_position["y"] == window.pos_y + 1 and window.in_use:
            window.activate_path_edit()
        elif isinstance(window, ExplorerWindow) and window.in_use and window.open_selected():
            pass
        else:
            window.activate_use()

    windows.move_to_end(id, last=False)


def cursor_deselect(_=None):
    id = last_id["value"]
    if id in windows:
        window = windows[id]
        window.selected = False
        if hasattr(window, "deactivate_use"):
            window.deactivate_use()


def cursor_popup():
    popup_button_id = overlapped_popup_button()
    if popup_button_id is None:
        return

    popups[0].content[overlapped_popup_button()]()
    popups.pop(0)
