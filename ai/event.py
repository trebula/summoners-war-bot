import cv2
import logging
import pyautogui
import time
from collections.abc import Generator
from .util.screen_util import (
    click,
    is_on_screen,
)
from .util.images import Images
from .util.img_reader_util import find_all_images
from .util.ocr import click_all_words


def collect_event_drops() -> None:
    """Collects event rewards."""
    click(Images.EVENT)
    time.sleep(2)
    for loc in _find_event():
        _collect_event(loc)
    # exit event
    click(Images.EVENT_X)


def _find_event() -> Generator[tuple, None, None]:
    """Finds events that have a drop available."""
    for i in range(3):
        gift_locs, _ = find_all_images(cv2.imread(Images.GIFT.value))
        for loc in gift_locs:
            yield loc
            # clicking an event banner and then backing out resets the
            # page position to the top, so we have to drag down again
            for _ in range(i):
                pyautogui.moveTo(720, 860)
                pyautogui.dragTo(720, 120, button="left", duration=1)

        pyautogui.moveTo(720, 860)
        pyautogui.dragTo(720, 120, button="left", duration=1)


def _collect_event(loc: tuple) -> None:
    coords = pyautogui.center(loc)
    # halve since mac retina displays are double resolution
    x, y = (coords.x / 2, coords.y / 2)
    pyautogui.click(x, y)
    logging.info("Collecting event rewards.")
    time.sleep(5)

    times = 0
    while times < 10:
        click_all_words("collect")
        if is_on_screen(Images.BACK_TO_TOP):
            break
        # have to scroll down instead of drag down
        pyautogui.scroll(-90)
        times += 1
        time.sleep(1)
    # exit event
    pyautogui.click(115, 35)
    time.sleep(5)
