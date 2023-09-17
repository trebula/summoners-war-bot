import logging
import pyautogui
import time
from .util.screen_util import (
    click,
    click_all,
    click_until_menu,
    is_on_screen,
    close_menus,
)
from .util.images import Images


def collect_resources() -> None:
    """Collects mana and crystals from the mines."""
    click_all(Images.MANA, times=2)
    time.sleep(1)
    click(Images.CRYSTAL_MINE)
    time.sleep(1)
    # click to unfocus any selected building
    pyautogui.click(240, 850)
    time.sleep(1)


def wish() -> None:
    """Use daily wishes."""
    opened_menu = click_until_menu(Images.WISH, Images.WISHES, interval=0)
    if not opened_menu:
        logging.warning("Failed to open wish menu.")
        return
    time.sleep(1)

    while True:
        if is_on_screen(Images.NO_WISHES):
            break
        if click_until_menu(
            Images.MAKE_WISH, Images.WISH_YES, retries=1, interval=1
        ):
            logging.info("Made a wish.")
            time.sleep(20)
            pyautogui.click(1100, 200, clicks=10, interval=1)
        else:
            break

    # exit wish menu
    close_menus()

    # reset screen to center
    pyautogui.moveTo(1000, 200)
    pyautogui.dragTo(880, 110, button="left", duration=1)
    logging.info("Reset screen to center.")


def guild_check_in() -> None:
    """Checks in to guild."""
    click(Images.COMMUNITY)
    click(Images.CHECK_IN)
    click(Images.COLLECT)
    click(Images.CHECK_IN_OK)
    close_menus()


def gift_friends() -> None:
    """Gifts friends."""
    click(Images.COMMUNITY)
    click(Images.FRIEND)
    click(Images.SEND_ALL)
    time.sleep(5)
    click(Images.OK)
    close_menus()


def collect_inbox() -> None:
    """Collects inbox rewards."""
    click(Images.INBOX)
    click(Images.GUILD_INBOX)
    click(Images.INBOX_COLLECT, times=10, interval=0.2)
    click_all(Images.INBOX_COLLECT)
    click(Images.SOCIAL_POINTS)
    click(Images.COLLECT_ALL)
    close_menus()


def collect_missions() -> None:
    """Collects daily missions."""
    click(Images.MISSION)
    times = 0
    while click(Images.MISSION_COLLECT) and times < 10:
        click(Images.GET)
        times += 1
    close_menus()


def powerup_rune() -> None:
    """Powers up a rune for the daily mission."""
    click(Images.MONSTER)
    click(Images.RUNE)
    click(Images.MANAGE)
    while not click(Images.RUNE_BOTTOM):
        # drag down
        pyautogui.moveTo(1000, 850)
        pyautogui.dragTo(1000, 440, button="left", duration=1)
    click(Images.POWERUP)
    click(Images.POWERUP_BUTTON)
    close_menus()


def summon_mons() -> None:
    """Summons monsters for the daily mission."""
    click_until_menu(Images.SUMMONHENGE, Images.SUMMON)
    click(Images.OK)
    click(Images.YES)
    # drag down
    pyautogui.moveTo(1100, 700)
    pyautogui.dragTo(1100, 50, button="left", duration=1)
    click(Images.SOCIAL_SUMMON)
    for _ in range(3):
        click(Images.SINGLE_SUMMON)
        click(Images.YES)
        time.sleep(15)
        click(Images.OK)
    close_menus()
    # reset screen to center
    pyautogui.moveTo(720, 500)
    pyautogui.dragTo(420, 300, button="left", duration=1)
    logging.info("Reset screen to center.")
