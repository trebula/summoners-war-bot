import cv2
import logging
import numpy as np
import pyautogui
import time
from collections.abc import Generator
from .util.screen_util import (
    click,
    click_until_menu,
    is_on_screen,
    close_menus,
)
from .util.images import Images
from .util.img_reader_util import find_all_images, non_max_suppression


reward_priority = [
    Images.DETERMINATION,
    Images.RAGE,
    Images.FATAL,
    Images.ENERGY,
]


def do_labyrinth() -> None:
    """Completes the labyrinth battles."""
    click_until_menu(Images.GUILD_TOWER, Images.GUILD_BATTLE)
    time.sleep(1)

    # scroll down to the bottom
    pyautogui.moveTo(1000, 500)
    pyautogui.dragTo(1000, 300, button="left", duration=1)

    click(Images.LABYRINTH)
    time.sleep(2)

    # drag up to the top right
    for _ in range(5):
        _drag_up()
        time.sleep(1)
    _drag_right()
    time.sleep(1)

    num_empty_lanterns = 0
    for locs in _find_new_labyrinth_portals():
        if num_empty_lanterns == 5:
            break
        for loc in locs:
            empty_lanterns, _ = find_all_images(
                cv2.imread(Images.EMPTY_LANTERN.value)
            )
            num_empty_lanterns = len(empty_lanterns)
            if num_empty_lanterns == 5:
                break
            battle_started = _start_labyrinth_battle(loc)
            if battle_started:
                time.sleep(60)  # wait for battle to finish
                while not click(Images.REWARD):
                    time.sleep(10)
                _select_reward()
                time.sleep(1)
                logging.info("Completed labyrinth battle.")
    # exit labyrinth
    click(Images.BACK)
    click(Images.BACK2)
    _reset_camera()


def do_rival_battles() -> None:
    """Completes the guild rival battles."""
    click_until_menu(Images.GUILD_TOWER, Images.GUILD_BATTLE)
    time.sleep(1)

    # scroll down to the bottom
    pyautogui.moveTo(1000, 500)
    pyautogui.dragTo(1000, 300, button="left", duration=1)

    click(Images.GUILD_RIVAL)
    time.sleep(2)

    num_battles = 0
    for locs in _find_new_rivals():
        if num_battles >= 3:
            break
        for loc in locs:
            if num_battles >= 3:
                break
            _complete_rival_battle(loc)
            num_battles += 1
    click(Images.BACK)
    _reset_camera()


def _find_new_labyrinth_portals() -> Generator[list, None, None]:
    """Looks for open labyrinth portals."""
    for _ in _drag_to_new_labyrinth_area():
        portal_locs = []
        confidences = []
        for i in range(4):
            portal_num = "LABYRINTH_PORTAL" + str(i + 1)
            # get the value of the image
            new_locs, new_confidences = find_all_images(
                cv2.imread(Images[portal_num].value), stop_confidence=0.85
            )
            portal_locs.extend(new_locs)
            confidences.extend(new_confidences)
        locs = np.c_[portal_locs, confidences]
        portal_locs, _ = non_max_suppression(locs, overlapThresh=0)
        if len(portal_locs) > 0:
            yield portal_locs


def _find_new_rivals() -> Generator[list, None, None]:
    """Looks for new rivals to battle."""
    for _ in _drag_across_rival_area():
        locs, _ = find_all_images(
            cv2.imread(Images.BASE.value), stop_confidence=0.85
        )
        if len(locs) > 0:
            yield locs


def _drag_to_new_labyrinth_area() -> Generator[None, None, None]:
    """Drags to a new screen with a new set of labyrinths."""
    yield None
    for _ in range(3):
        yield _drag_left()
        yield _drag_down()
        yield _drag_right()
        yield _drag_down()


def _drag_across_rival_area() -> Generator[None, None, None]:
    """Drags to a new screen with a new set of rivals."""
    yield None
    for _ in range(3):
        yield _drag_right()


def _start_labyrinth_battle(loc: tuple) -> bool:
    """Battles the labyrinth at the given location."""
    coords = pyautogui.center(loc)
    # halve since mac retina displays are double resolution
    x, y = (coords.x / 2, coords.y / 2)
    pyautogui.click(x, y)
    time.sleep(1)
    if is_on_screen(Images.DECREASE_AS):
        logging.info(
            "Setting decrease attack speed labyrinth difficulty to easy."
        )
        click(Images.DIFFICULTY)
        time.sleep(1)
        click(Images.EASY)
        time.sleep(1)
    else:
        click(Images.DIFFICULTY)
        time.sleep(1)
        click(Images.NORMAL)
        time.sleep(1)
    click(Images.LABYRINTH_BATTLE)
    time.sleep(5)

    # check if already won battle
    if click(Images.OK):
        logging.info("Already won battle.")
        time.sleep(1)
        close_menus()
        time.sleep(1)
        return False

    click(Images.START_BATTLE)
    logging.info("Started labyrinth battle.")
    time.sleep(20)  # long sleep in case enemy attacks first
    click(Images.LABYRINTH_AUTOPLAY)
    return True


def _complete_rival_battle(loc: tuple) -> None:
    """Battles the rival at the given location."""
    coords = pyautogui.center(loc)
    # halve since mac retina displays are double resolution
    x, y = (coords.x / 2, coords.y / 2)
    pyautogui.click(x, y)
    time.sleep(1)
    click(Images.RIVAL_ATTACK)
    time.sleep(1)
    click(Images.START_BATTLE)
    logging.info("Started rival battle.")
    time.sleep(20)  # long sleep in case enemy attacks first
    click(Images.RIVAL_AUTOPLAY)
    time.sleep(30)  # wait for battle to finish
    # start second battle when possible
    while not click(Images.RIVAL_AUTOPLAY):
        time.sleep(10)
    logging.info("Started second rival battle.")
    time.sleep(30)  # wait for battle to finish
    while not click(Images.RIVAL_FINISH):
        time.sleep(10)
    logging.info("Finished rival battle.")
    time.sleep(1)


def _select_reward() -> None:
    """Selects a reward from the labyrinth."""
    for reward in reward_priority:
        if click(reward, confidence=0.7):
            logging.info("Selected %s rune.", reward.name)
            time.sleep(5)
            close_menus()
            time.sleep(5)
            return
    logging.info("No preferred runes found.")
    pyautogui.click(720, 320)
    time.sleep(5)
    close_menus()
    time.sleep(5)


def _reset_camera() -> None:
    close_menus()
    # reset screen to center
    pyautogui.moveTo(400, 500)
    pyautogui.dragTo(670, 320, button="left", duration=1)


def _drag_left() -> None:
    """Drags to the left."""
    pyautogui.moveTo(100, 450)
    pyautogui.dragTo(1300, 450, button="left", duration=1)


def _drag_right() -> None:
    """Drags to the right."""
    pyautogui.moveTo(1300, 450)
    pyautogui.dragTo(100, 450, button="left", duration=1)


def _drag_up() -> None:
    """Drags up."""
    pyautogui.moveTo(720, 150)
    pyautogui.dragTo(720, 750, button="left", duration=1)


def _drag_down() -> None:
    """Drags down."""
    pyautogui.moveTo(720, 750)
    pyautogui.dragTo(720, 150, button="left", duration=1)
