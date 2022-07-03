"""Automatic trait selection in Hunt: Showdown from presets.

Requirements:
    pip install keyboard pyautogui pygetwindow pillow

"""

import ui_automation
from gui import launch_gui


def main():
    @ui_automation.skipped_by_escape_key
    def equip_selected_traits(selected_traits: list):
        if not ui_automation.set_hunt_showdown_as_foreground_window():
            # Hunt does not seem to run.
            return
        for trait in selected_traits:
            ui_automation.add_trait(trait["name"])

    launch_gui(equipTraitsCallback=equip_selected_traits)


main()
