from pathlib import Path

from window import new_window, delete_window, Window, TextWindow, ExplorerWindow
from cursor import get_last_id, cursor_select
from variables import cursor_position, home_path


desktop_popup = {
    "New window": lambda: new_window(cursor_position["y"], cursor_position["x"], Window),
    "New text file": lambda: new_window(cursor_position["y"], cursor_position["x"], TextWindow),
    "File explorer": lambda: new_window(cursor_position["y"], cursor_position["x"], ExplorerWindow, home_path)
}

window_popup = {
    "Delete window": lambda: delete_window(get_last_id()),
    "Select window": lambda: cursor_select(True),
    "Use window": lambda: cursor_select(True, True)
}
