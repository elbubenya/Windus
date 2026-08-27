from window import new_window, delete_window, Window, TextWindow
from cursor import get_last_id, cursor_select
from variables import cursor_position


desktop_popup = {
    "New window": lambda: new_window(cursor_position["y"], cursor_position["x"], Window),
    "New text file": lambda: new_window(cursor_position["y"], cursor_position["x"], TextWindow)
}

window_popup = {
    "Delete window": lambda: delete_window(get_last_id()),
    "Select window": lambda: cursor_select(True)
}
