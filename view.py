import menu_strings
from math import ceil
from functools import partial
from menu import Menu, NumberMenu, IndexMenu, ItemMenu


class View:

    TaskMenu = partial(ItemMenu, **menu_strings.task_config)
    main_menu = IndexMenu(**menu_strings.main_config)
    name_menu = Menu(**menu_strings.name_config)
    minutes_menu = NumberMenu(**menu_strings.minutes_config)
    notes_menu = Menu(**menu_strings.notes_config)
    find_menu = IndexMenu(**menu_strings.find_config)
    match_menu = Menu(**menu_strings.match_config)

    def main_menu_prompt(self):
        choice = self.main_menu.run()
        return choice

    def find_prompt(self):
        method = self.find_menu.run()
        return method

    def match_prompt(self):
        phrase = self.match_menu.run()
        return phrase

    def add_entry_prompt(self):
        name = self.name_menu.run()
        minutes = self.minutes_menu.run()
        notes = self.notes_menu.run()
        return name, minutes, notes

    def task_prompt(self, tasks):
        task_menu = self.TaskMenu(items=tasks, key="name")
        task = task_menu.run()
        return task

    def print_task(self, task):
        line_length = 30
        print("\033c", end="")
        print(task["date"])
        print("Task: {}".format(task["name"]))
        print("=" * 30 + "\n")
        for index in range(ceil(len(task["notes"])/line_length)):
            start = index * line_length
            end = start + line_length
            print(task["notes"][start:end])
        print("")
        print("Task duration: {} minutes".format(task["minutes"]))
        print("")
        input("(Press enter to continue)")
