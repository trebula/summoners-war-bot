from .img_reader_util import find_image, find_all_images
from .images import Images
import pyautogui
import numpy as np
import cv2
import time
import logging


def click(
    image: Images,
    haystack_image=None,
    times: int = 1,
    confidence: float = 0.8,
    interval: float = 2,
):
    """Clicks the image once.

    Args:
        image (Images): The image to click.
        haystack_image (np.array, optional): The haystack image to search in.
            Defaults to None, which ends up searching the entire screen.
        times (int, optional): The number of times to click. Defaults to 1.

    Returns:
        bool: True if image was found, False otherwise
    """
    # get image np array
    img = cv2.imread(image.value)
    loc, _ = find_image(
        img, haystack_image, stop_confidence=confidence, scales=[]
    )
    if loc:
        # click on the center of the image n times
        coords = pyautogui.center(loc)
        # halve since mac retina displays are double resolution
        x, y = (
            coords.x / 2,
            coords.y / 2,
        )
        pyautogui.click(x, y, clicks=times, interval=interval)
        time.sleep(1)
        return True
    else:
        logging.info("Image %s not found.", image.name)
        return False


def click_until_menu(
    image: Images, menu_image: Images, retries: int = 3, interval: int = 10
):
    """Clicks the image until the related menu opens, and then clicks the menu button.

    Args:
        image (Images): The image to click.
        retries (int, optional): The number of times to retry. Defaults to 3.
        interval (int, optional): The interval in seconds between retries. Defaults to 10.

    Returns:
        bool: True if image was found, False otherwise
    """
    for _ in range(retries):
        if click(image, times=2):
            # look for the menu
            if click(menu_image):
                return True
        time.sleep(interval)
    return False


def click_all(image: Images, times: int = 1):
    """Clicks all instances of the image.

    Args:
        image (Images): The image to click.

    Returns:
        bool: True if image was found, False otherwise
    """
    # get image np array
    img = cv2.imread(image.value)
    locs, _ = find_all_images(img)
    if len(locs) > 0:
        # click on the center of each image
        for loc in locs:
            coords = pyautogui.center(loc)
            # halve since mac retina displays are double resolution
            x, y = (coords.x / 2, coords.y / 2)
            pyautogui.click(x, y, clicks=times, interval=0.5)
            pyautogui.sleep(0.5)
        return True
    else:
        logging.info("Image %s not found.", image.name)
        return False


def is_on_screen(image: Images):
    """Checks if there are no more wishes."""
    img = cv2.imread(image.value)
    loc, _ = find_image(img, stop_confidence=0.8, scales=[])
    if loc:
        logging.info("Found image %s.", image.name)
        return True
    else:
        logging.info("Image %s not found.", image.name)
        return False


def close_menus():
    num_closed = 0
    while num_closed < 5 and (
        click_all(Images.X)
        or click_all(Images.AD_X)
        or click_all(Images.RUNE_X)
        or click_all(Images.MENU_X)
    ):
        num_closed += 1
        pyautogui.sleep(2)
