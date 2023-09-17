import logging
import pyautogui
import time
from .util.screen_util import click, close_menus
from .util.images import Images


def login() -> None:
    """Logs into the game by clicking through the menus.

    Need to close the startup banners and then click anywhere on the
    screen to start the game.
    """
    # close startup banners
    while click(Images.LOGIN_X):
        logging.info("Closed startup banner.")
        time.sleep(1)

    # click anywhere to start the game
    pyautogui.click(700, 400)
    logging.info("Clicked to start the game.")
    time.sleep(5)

    close_menus()
