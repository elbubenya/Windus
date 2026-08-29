import os
import time
import keyboard

from keyboard_input_handler import handle_text_input
from window import reset_windows
from explorer_window import path_back
from variables import windows, popups, cursor_position, directions, key_state, window_used, text_input, main_key, alt_action_key, deselect_key, last_id
from popup import new_popup
from cursor import cursor_move, cursor_select, cursor_deselect, cursor_popup, \
                   overlapped_window_id, overlapped_popup_button
from popup_templates import desktop_popup, window_popup
from render import render


def track_key(key):
    keyboard.on_press_key(key, lambda _: key_state.__setitem__(key, True))
    keyboard.on_release_key(key, lambda _: key_state.__setitem__(key, False))


def handle_left_arrow(_):
    if not text_input["value"]:
        path_back(windows.get(last_id["value"]))


def handle_enter(_):
    window_popup_open = bool(popups) and popups[0].content is window_popup

    if not window_used["value"] and not text_input["value"]:
        if overlapped_popup_button() is not None:
            cursor_popup()
        elif overlapped_window_id() is not None and not window_popup_open:
            if not key_state[alt_action_key]:
                if not overlapped_window_id()[1]:
                    cursor_select()
                else:
                    windows.pop(overlapped_window_id()[0])
                if popups:
                    popups.pop(0)
            else:
                new_popup(window_popup, cursor_position["y"], cursor_position["x"] + 1)
                reset_windows()
        else:
            if popups:
                popups.pop(0)
            elif not any(window.selected for window in windows.values()):
                new_popup(desktop_popup, cursor_position["y"], cursor_position["x"] + 1)
            reset_windows()


def main():
    if not window_used["value"] and not text_input["value"]:
        dy, dx = cursor_move(key_state)

        if not popups:
            for window in windows.values():
                if key_state[alt_action_key]:
                    window.scale_window(key_state)
                else:
                    window.move_window(dy, dx)

    if text_input["value"]:
        handle_text_input()

    render()
    time.sleep(0.075)


if __name__ == "__main__":
    keyboard.on_press_key(main_key, handle_enter)
    keyboard.on_press_key(deselect_key, cursor_deselect)
    keyboard.on_press_key("left", handle_left_arrow)
    for tracked_key in list(directions) + [alt_action_key]:
        track_key(tracked_key)
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        main()