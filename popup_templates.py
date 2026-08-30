from window import new_window, delete_window
from textbox_module import TextboxModule
from explorer_module import ExplorerModule
from cursor import cursor_select
from variables import cursor_position, default_path, last_id


desktop_popup = {
    "New window": lambda: new_window(cursor_position["y"], cursor_position["x"]),
    "New text file": lambda: new_window(cursor_position["y"], cursor_position["x"], TextboxModule),
    "File explorer": lambda: new_window(cursor_position["y"], cursor_position["x"], ExplorerModule, default_path)
}

window_popup = {
    "Delete window": lambda: delete_window(last_id["value"]),
    "Transform window": lambda: cursor_select(True),
    "Select window": lambda: cursor_select(True, True)
}
