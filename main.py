import os
import time
import keyboard

from variables import windows, popups, cursor_position, directions, key_state, window_used
from popup import new_popup
from cursor import cursor_move, cursor_select, cursor_unselect, cursor_popup, \
                   overlapped_window_id, overlapped_popup_button
from popup_templates import desktop_popup, window_popup
from render import render


def track_key(key):
    keyboard.on_press_key(key, lambda _: key_state.__setitem__(key, True))
    keyboard.on_release_key(key, lambda _: key_state.__setitem__(key, False))


def handle_enter(_):
    window_popup_open = bool(popups) and popups[0].content is window_popup

    if not window_used["value"]:
        if overlapped_popup_button() is not None:
            cursor_popup()
        elif overlapped_window_id() is not None and not window_popup_open:
            if not key_state["shift"]:
                if not overlapped_window_id()[1]:
                    cursor_select()
                else:
                    windows.pop(overlapped_window_id()[0])
                if popups:
                    popups.pop(0)
            else:
                new_popup(window_popup, cursor_position["y"], cursor_position["x"] + 1)
                list(map(lambda window: setattr(window, "selected", 0), windows.values()))
        else:
            if popups:
                popups.pop(0)
            elif not any(window.selected for window in windows.values()):
                new_popup(desktop_popup, cursor_position["y"], cursor_position["x"] + 1)
            list(map(lambda window: setattr(window, "selected", 0), windows.values()))


def main():
    if not window_used["value"]:
        dy, dx = cursor_move(key_state)

        if not popups:
            for window in windows.values():
                if key_state["shift"]:
                    window.scale_window(key_state)
                else:
                    window.move_window(dy, dx)

    render()
    time.sleep(0.075)


if __name__ == "__main__":
    keyboard.on_press_key("enter", handle_enter)
    keyboard.on_press_key("esc", cursor_unselect)
    for tracked_key in list(directions) + ["shift"]:
        track_key(tracked_key)
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        main()