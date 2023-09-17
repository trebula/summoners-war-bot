import logging
import numpy as np
import pyautogui
import time
import cv2
from .util.screen_util import click, click_until_menu, close_menus
from .util.images import Images

USEFUL_ITEMS = [
    Images.MYSTICAL_SCROLL,
    # Images.SILVER_2STAR,
    # Images.UNKNOWN_SCROLL,
]


def buy_items_from_shop():
    """Buys useful items from magic shop."""
    # open magic shop
    if not click_until_menu(Images.MAGIC_SHOP, Images.PURCHASE):
        logging.error("Failed to open magic shop.")
        return
    time.sleep(1)

    # create temporary image that only contains the shop items
    shop = np.array(pyautogui.screenshot())

    # fill the left half of the image with black
    half = shop.shape[1] // 2
    shop[:, :half] = 0

    # convert to pillow image
    shop = cv2.cvtColor(shop, cv2.COLOR_BGR2RGB)

    # buy items
    for item in USEFUL_ITEMS:
        while click(item, shop):
            didClick = click(Images.BUY)
            click(Images.YES)  # in case monster goes to storage
            didClick = didClick and click(Images.SHOP_YES)
            if not didClick:
                logging.error("Failed to buy item: %s", item.name)
                break
            logging.info("Bought item: %s", item.name)
            time.sleep(1)

    # close magic shop
    close_menus()

    # reset screen to center
    pyautogui.moveTo(400, 250)
    pyautogui.dragTo(650, 300, button="left", duration=1)
    logging.info("Reset screen to center.")
