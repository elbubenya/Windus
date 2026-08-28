from variables import windows, popups, cursor_position, last_id, directions, resolution


def cursor_move(pressed):
    old_y, old_x = cursor_position["y"], cursor_position["x"]

    for key, (dy, dx) in directions.items():
        if pressed[key]:
            cursor_position["y"] += dy
            cursor_position["x"] += dx

    cursor_position["y"] = min(max(cursor_position["y"], 0), resolution["y"]-1)
    cursor_position["x"] = min(max(cursor_position["x"], 0), resolution["x"]-1)

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


def get_last_id():
    return last_id["value"]


def overlapped_popup_button():
    for popup in popups.values():
        for y, button in enumerate(popup.content):
            if (popup.pos_y + y == cursor_position["y"] and
                    popup.pos_x <= cursor_position["x"] < popup.pos_x + popup.res_x):
                return button
    return None


def cursor_select(ignore_popups=False):
    if last_id["value"] is None or (overlapped_popup_button() is not None and not ignore_popups):
        return

    id = last_id["value"]
    windows[id].selected = 1 - windows[id].selected
    windows.move_to_end(id, last=False)


def cursor_popup():
    popup_button_id = overlapped_popup_button()
    if popup_button_id is None:
        return

    popups[0].content[overlapped_popup_button()]()
    popups.pop(0)
