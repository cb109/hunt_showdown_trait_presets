import ctypes
import os
import random
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from typing import Tuple, Optional, Union

import keyboard
import pyautogui
import pygetwindow
from PIL import ImageDraw

GAME_WINDOW_TITLE = "Hunt: Showdown"
COLOR_GREEN = (0, 255, 0)
CAPTURE2TEXT_CLI_BINARY = "Capture2Text/Capture2Text_CLI.exe"


@dataclass
class UIElement:
    """A coordinate or rectangle designating a specific Hunt UI element."""

    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None


# Measured for a screen of 2560x1080px
UI_UPGRADE_POINTS = UIElement(x=422, y=898, width=60, height=50)
UI_TRAITS_SEARCH_INPUT = UIElement(x=980, y=225)
UI_TRAITS_FIRST_MATCH = UIElement(x=775, y=395)
UI_TRANSACTION_FAILED_DIALOG_OK_BTN = UIElement(x=1235, y=735)


def debug_upgrade_points_rectangle_with_screenshot():
    """Create screenshot with coordinates overlayed and display it.

    Screenshots work best with Hunt in Window Mode 'Borderless'.

    """

    # Allow screenshot even if Hunt is not running.
    set_hunt_showdown_as_foreground_window()

    tempdir = tempfile.gettempdir()
    screenshot_filepath = os.path.join(
        tempdir, f"hunt_showdown_trait_presets_screenshot_{uuid.uuid4()}.png"
    )
    with open(screenshot_filepath, "w") as f:
        f.write("")
    screenshot_filepath = os.path.abspath(screenshot_filepath)

    image = pyautogui.screenshot()
    drawing = ImageDraw.Draw(image)

    x = UI_UPGRADE_POINTS.x
    y = UI_UPGRADE_POINTS.y
    width = UI_UPGRADE_POINTS.width
    height = UI_UPGRADE_POINTS.height

    drawing.rectangle(
        (
            (x, y),
            (x + width, y + height),
        ),
        outline=COLOR_GREEN,
    )
    image.save(screenshot_filepath)

    put_hunt_showdown_window_to_background()
    subprocess.run(["explorer", screenshot_filepath], shell=True)


def get_ocr_text_from_screen_rectangle(x: int, y: int, width: int, height: int) -> str:
    args = [
        CAPTURE2TEXT_CLI_BINARY,
        "-l",
        "English",
        "--screen-rect",
        f"{x} {y} {x + width} {y + height}",
    ]
    return subprocess.check_output(args)


def get_upgrade_points_from_screenshot() -> Optional[int]:
    set_hunt_showdown_as_foreground_window()

    def _handle_common_mistakes(text):
        return (
            text.decode("utf-8")
            .replace(r"\r\n", "")
            .replace(")", "")
            .replace("(", "")
            .replace(".", "")
            .replace("'", "")
        )

    text = get_ocr_text_from_screen_rectangle(
        UI_UPGRADE_POINTS.x,
        UI_UPGRADE_POINTS.y,
        UI_UPGRADE_POINTS.width,
        UI_UPGRADE_POINTS.height,
    )
    text = _handle_common_mistakes(text)
    try:
        return int(text)
    except ValueError:
        print(f"Could not recognize upgrade points, got: {text}")
        return None


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
            print("skipped by esc")
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


def _search_for(text: str, clear_first: bool = True):
    if is_capslock_active():
        pyautogui.press("capslock")

    if clear_first:
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")

    pyautogui.write(text)
    pyautogui.press("enter")


def _search_for_trait(trait_name: str):
    smooth_move(UI_TRAITS_SEARCH_INPUT.x, UI_TRAITS_SEARCH_INPUT.y)
    pyautogui.doubleClick()
    _search_for(trait_name)


def _maybe_get_rid_of_failure_dialog():
    smooth_move(
        UI_TRANSACTION_FAILED_DIALOG_OK_BTN.x, UI_TRANSACTION_FAILED_DIALOG_OK_BTN.y
    )
    time.sleep(0.5)
    pyautogui.click()


def _add_first_matching_trait():
    smooth_move(UI_TRAITS_FIRST_MATCH.x, UI_TRAITS_FIRST_MATCH.y)
    pyautogui.doubleClick()


@skipped_by_escape_key
def add_trait(trait_name: str):
    _search_for_trait(trait_name)
    _add_first_matching_trait()
    _maybe_get_rid_of_failure_dialog()
