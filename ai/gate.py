import time
from enum import Enum
from .util.screen_util import click, click_until_menu, close_menus
from .util.images import Images


class GateBattles(Enum):
    SCENARIO = 0
    GIANTS = 1


def start_dimensions_gate(battle_type: GateBattles) -> None:
    click_until_menu(Images.DIMENSIONS_GATE, Images.REPEAT)
    if click(Images.REPLAY):
        click(Images.YES)
    else:
        click(Images.SELECT_DUNGEON)
        # handles "There are rewards to sort out." prompt
        click(Images.YES)
        if battle_type == GateBattles.SCENARIO:
            click(Images.SCENARIO)
            click(Images.SCENARIO_BATTLE)
        elif battle_type == GateBattles.GIANTS:
            click(Images.CAIROS)
            click(Images.GATE_BATTLE)
    if not click(Images.REPEAT_BATTLE):
        click(Images.START_BATTLE)
    time.sleep(5)
    click(Images.MINIMIZE)
    close_menus()
