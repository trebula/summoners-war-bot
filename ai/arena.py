import cv2
import logging
import pyautogui
import time
from .util.screen_util import (
    click,
    click_until_menu,
    is_on_screen,
    close_menus,
)
from .util.images import Images
from .util.img_reader_util import find_all_images


def do_arena() -> None:
    """Completes arena battles."""
    click_until_menu(Images.ARENA, Images.BATTLE_LOG)
    if (
        not _do_rival_battles()
        or not _do_revenge_battles()
        or not _do_matchup_battles()
    ):
        click(Images.BACK)
        close_menus()


def _do_rival_battles() -> bool:
    """Completes rival battles."""
    click(Images.RIVAL)

    # scroll down past Amir battle
    pyautogui.moveTo(700, 320)
    pyautogui.dragTo(700, 220, button="left", duration=1)
    if not _battle_rival():
        # no more invitations for battle
        return False

    # scroll down to next page
    pyautogui.moveTo(700, 670)
    pyautogui.dragTo(700, 210, button="left", duration=1)
    if not _battle_rival():
        # no more invitations for battle
        return False
    return True


def _battle_rival() -> bool:
    """Battles available rivals."""
    battle_locs, _ = find_all_images(cv2.imread(Images.ARENA_BATTLE.value))
    for loc in battle_locs:
        coords = pyautogui.center(loc)
        # halve since mac retina displays are double resolution
        x, y = (coords.x / 2, coords.y / 2)
        pyautogui.click(x, y)
        time.sleep(1)
        if _out_of_invitations():
            logging.info("No more arena invitations.")
            return False
        click(Images.START_BATTLE)
        logging.info("Starting arena rival battle.")
        time.sleep(20)
        click(Images.ARENA_AUTOPLAY)
        time.sleep(10)
        while not click(Images.ARENA_REWARD):
            time.sleep(10)
        logging.info("Arena rival battle finished.")
    return True


def _do_revenge_battles() -> bool:
    """Completes revenge battles."""
    click(Images.HISTORY)
    if not _battle():
        # no more invitations for battle
        return False

    # scroll down to next page
    pyautogui.moveTo(700, 730)
    pyautogui.dragTo(700, 150, button="left", duration=1)
    if not _battle():
        # no more invitations for battle
        return False
    return True


def _battle() -> bool:
    """Revenge battles opponents."""
    battle_locs, _ = find_all_images(cv2.imread(Images.ARENA_BATTLE.value))
    for loc in battle_locs:
        coords = pyautogui.center(loc)
        # halve since mac retina displays are double resolution
        x, y = (coords.x / 2, coords.y / 2)
        pyautogui.click(x, y)
        time.sleep(5)
        if _out_of_invitations():
            logging.info("No more arena invitations.")
            return False
        if not is_on_screen(Images.EMPTY_SLOT):
            logging.info(
                "Enemy team has no empty slots and might be too difficult - skipping battle."
            )
            click(Images.CANCEL)
            continue
        click(Images.START_BATTLE)
        logging.info("Starting arena rival battle.")
        time.sleep(20)
        click(Images.ARENA_AUTOPLAY)
        time.sleep(10)
        while not click(Images.ARENA_REWARD, times=2):
            time.sleep(10)
        logging.info("Arena rival battle finished.")
    return True


def _do_matchup_battles() -> bool:
    """Completes matchup battles."""
    click(Images.MATCHUP)
    retry = 0
    while retry < 5:
        if not _battle():
            # no more invitations for battle
            return False

        # scroll down to next page
        for _ in range(2):
            pyautogui.moveTo(700, 730)
            pyautogui.dragTo(700, 300, button="left", duration=1)
            if not _battle():
                # no more invitations for battle
                return False
        click(Images.REFRESH_LIST)
        click(Images.REFRESH)
        retry += 1
    return True


def _out_of_invitations() -> bool:
    if is_on_screen(Images.OUT_OF_ARENA):
        close_menus()
        return True
    return False
