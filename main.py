#!/usr/bin/env conda run -n summoners-war python

import logging
import time
import os
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import Button, Text, Scrollbar, END
from ai import (
    GateBattles,
    buy_items_from_shop,
    collect_event_drops,
    collect_inbox,
    collect_missions,
    collect_resources,
    do_arena,
    do_labyrinth,
    do_rival_battles,
    gift_friends,
    guild_check_in,
    login,
    powerup_rune,
    start_dimensions_gate,
    summon_mons,
    wish,
)


def idle():
    i = 0
    while True:
        if (i % 60) == 0:
            logging.info("Collecting resources.")
            collect_resources()
            buy_items_from_shop()
        start_dimensions_gate(GateBattles.GIANTS)
        i += 1
        time.sleep(60)


def summoners_war_bot():
    # open summoners war in fullscreen
    os.system("open -a Summoners\\ War.app")
    time.sleep(30)
    os.system(
        '/usr/bin/osascript -e "tell application \\"Summoners War.app\\""'
        ' -e "tell application \\"System Events\\""'
        ' -e "keystroke \\"f\\" using {control down, command down}"'
        ' -e "end tell"'
        ' -e "end tell"'
    )
    time.sleep(5)

    collect_inbox()
    collect_missions()
    login()
    collect_resources()
    start_dimensions_gate(GateBattles.SCENARIO)
    guild_check_in()
    gift_friends()
    powerup_rune()
    summon_mons()
    buy_items_from_shop()
    wish()
    do_labyrinth()
    do_rival_battles()
    do_arena()
    collect_event_drops()
    start_dimensions_gate(GateBattles.GIANTS)
    time.sleep(60)
    idle()


executor = ThreadPoolExecutor(max_workers=1)


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.configure(state="disabled")

        # Scroll to the end so we always see the latest log entry
        self.text_widget.see(tk.END)


def delayed_execution(func, delay=10):
    """Executes the function after a delay."""
    logging.info(f"Executing {func.__name__} in {delay} seconds.")
    time.sleep(delay)
    func()
    logging.info(f"Finished executing {func.__name__}.")


def queue_task(func):
    """Queue the task to be executed after a delay."""
    executor.submit(delayed_execution, func)


# Function to handle the button click
def stop_program(root):
    logging.shutdown()
    root.destroy()
    os._exit(0)


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create a basic window and set its size
    root = tk.Tk()
    root.title("Bot Controls")
    root.geometry("1000x800")

    # Create a frame for the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20, padx=20)

    tasks = [
        ("Start Bot", summoners_war_bot),
        ("Collect Inbox", lambda: queue_task(collect_inbox)),
        ("Collect Missions", lambda: queue_task(collect_missions)),
        ("Login", lambda: queue_task(login)),
        ("Collect Resources", lambda: queue_task(collect_resources)),
        (
            "Start Giants Dimensions Gate",
            lambda: queue_task(
                lambda: start_dimensions_gate(GateBattles.GIANTS)
            ),
        ),
        ("Guild Check In", lambda: queue_task(guild_check_in)),
        ("Gift Friends", lambda: queue_task(gift_friends)),
        ("Powerup Rune", lambda: queue_task(powerup_rune)),
        ("Summon Mons", lambda: queue_task(summon_mons)),
        ("Buy Items From Shop", lambda: queue_task(buy_items_from_shop)),
        ("Wish", lambda: queue_task(wish)),
        ("Do Labyrinth", lambda: queue_task(do_labyrinth)),
        ("Do Rival Battles", lambda: queue_task(do_rival_battles)),
        ("Do Arena", lambda: queue_task(do_arena)),
        ("Collect Event Drops", lambda: queue_task(collect_event_drops)),
        ("Idle", lambda: queue_task(idle)),
    ]

    num_columns = 4
    for index, (task_name, task_func) in enumerate(tasks):
        row, col = divmod(index, num_columns)
        button = Button(
            button_frame, text=task_name, command=task_func, width=20
        )
        button.grid(row=row, column=col, padx=5, pady=5)

    # Create a Text widget to display log messages
    log_text = Text(root, wrap=tk.WORD, state=tk.DISABLED, height=15)
    log_text.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

    # Add a scrollbar to the Text widget
    scrollbar = Scrollbar(log_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=log_text.yview)

    # Add the custom logging handler
    handler = TextHandler(log_text)
    logging.getLogger().addHandler(handler)

    # Close button positioned at the bottom
    close_button = Button(
        root, text="Close", command=lambda: stop_program(root)
    )
    close_button.pack(pady=20)

    # Run the GUI in the main thread
    root.mainloop()


if __name__ == "__main__":
    main()
