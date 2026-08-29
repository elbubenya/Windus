from window import new_window, delete_window, Window, TextWindow, ExplorerWindow
from cursor import cursor_select
from variables import cursor_position, standart_path, last_id


desktop_popup = {
    "New window": lambda: new_window(cursor_position["y"], cursor_position["x"], Window),
    "New text file": lambda: new_window(cursor_position["y"], cursor_position["x"], TextWindow),
    "File explorer": lambda: new_window(cursor_position["y"], cursor_position["x"], ExplorerWindow, standart_path)
}

window_popup = {
    "Delete window": lambda: delete_window(last_id["value"]),
    "Select window": lambda: cursor_select(True),
    "Use window": lambda: cursor_select(True, True)
}
