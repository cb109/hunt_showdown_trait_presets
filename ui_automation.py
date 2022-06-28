import ctypes
import random
from typing import Tuple, Optional, Union

import keyboard
import pyautogui
import pygetwindow

GAME_WINDOW_TITLE = "Hunt: Showdown"


def is_capslock_active() -> bool:
    # https://stackoverflow.com/a/21160382
    VK_CAPITAL = 0x14
    user32 = ctypes.windll.user32
    return user32.GetKeyState(VK_CAPITAL) > 0


def get_screen_size() -> Tuple[int, int]:
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def skipped_by_escape_key(func):
    """Skip function call when escape key is being pressed.

    Use as a function decorator.

    """

    def inner(*args, **kwargs):
        if keyboard.is_pressed("esc"):
            return
        return func(*args, **kwargs)

    return inner


@skipped_by_escape_key
def set_hunt_showdown_as_foreground_window() -> bool:
    game_window = None
    for window in pygetwindow.getWindowsWithTitle(GAME_WINDOW_TITLE):
        if window.title == GAME_WINDOW_TITLE:
            game_window = window
            break
    if not game_window:
        message = f"Window titled '{GAME_WINDOW_TITLE}' could not be found"
        print(message)
        return False

    game_window.minimize()
    game_window.restore()

    return True


@skipped_by_escape_key
def put_hunt_showdown_window_to_background() -> bool:
    game_window = None
    for window in pygetwindow.getWindowsWithTitle(GAME_WINDOW_TITLE):
        if window.title == GAME_WINDOW_TITLE:
            game_window = window
            break
    if not game_window:
        message = f"Window titled '{GAME_WINDOW_TITLE}' could not be found"
        print(message)
        return False

    game_window.minimize()

    return True


@skipped_by_escape_key
def smooth_move(
    x: Union[str, int],
    y: Union[str, int],
    random_offset_up_to: int = 0,
    seconds: Optional[float] = 0.0,
    tween: bool = False,
):
    x = int(x)
    y = int(y)

    offset_x, offset_y = 0, 0
    if random_offset_up_to:
        offset_x = random.randint(-random_offset_up_to, random_offset_up_to)
        offset_y = random.randint(-random_offset_up_to, random_offset_up_to)

    extra = []
    if tween:
        extra = [pyautogui.easeOutQuad]

    pyautogui.moveTo(
        x + offset_x,
        y + offset_y,
        seconds,
        *extra,
    )
