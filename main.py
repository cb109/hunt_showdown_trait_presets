"""Automatic trait selection in Hunt: Showdown from presets.

Requirements:
    pip install keyboard pyautogui pygetwindow pillow

"""

import ui_automation
from traits import TRAITS, get_trait_by_name

EXAMPLE_PRESET = (
    "Greyhound",
    "Doctor",
    "Physician",
    "Lightfoot",
    "Fanning",
    "Packmule",
    "Whispersmith",
)


def main():
    # ui_automation.debug_upgrade_points_rectangle_with_screenshot()

    # upgrade_points = ui_automation.get_upgrade_points_from_screenshot()
    # print("upgrade_points", upgrade_points)
    # if not upgrade_points:
    #     return

    # for trait_name in EXAMPLE_PRESET:
    #     trait = get_trait_by_name(trait_name)
    #     if upgrade_points >= trait["cost"]:
    #         ui_automation.add_trait(trait_name)
    #         upgrade_points = ui_automation.get_upgrade_points_from_screenshot()
    #         print("upgrade_points", upgrade_points)
    #     else:
    #         print(
    #             f"Cannot afford trait {trait_name}, only {upgrade_points} points left"
    #         )

    for trait_name in EXAMPLE_PRESET:
        ui_automation.add_trait(trait_name)


main()
