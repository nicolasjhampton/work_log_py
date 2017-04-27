import menu_strings
import inspect
from math import ceil
from functools import partial, wraps
from collections import OrderedDict
from datetime import datetime
from menu import Menu, NumberMenu, IndexMenu, ItemMenu, OptionMenu


class View:

    TaskMenu = partial(ItemMenu, **menu_strings.task_config)
    name_menu = Menu(**menu_strings.name_config)
    minutes_menu = NumberMenu(**menu_strings.minutes_config)
    notes_menu = Menu(**menu_strings.notes_config)
    find_menu = IndexMenu(**menu_strings.find_config)
    match_menu = Menu(**menu_strings.match_config)

    menus = {
        "text": Menu(**menu_strings.match_config),
        "key": partial(ItemMenu, **menu_strings.task_config)
    }

    def __init__(self, cont):
        self.main_menu = {}
        self.main_menu["options"] = OrderedDict()
        self.main_menu["message"] = cont.__class__.__doc__
        for name, func in inspect.getmembers(cont, predicate=inspect.ismethod):
            input(name)
            if name[-6:] == "option":
                self.main_menu["options"][name[0]] = func
        input(self.main_menu)
        self.main_menu = OptionMenu(**self.main_menu)

    def main_menu_prompt(self):
        choice = self.main_menu.run()
        return choice

    def pre_prompt(menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records):
                menu_input = {}
                prompt = self.view.menus[menu_type]
                menu_input["phrase"] = prompt.run()
                return func(self, records, **menu_input)
            return method
        return wrapper

    def post_prompt(menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records):
                tasks = func(self, records)
                task_menu = self.view.menus[menu_type](items=tasks, key="name")
                task = task_menu.run()
                return task
            return method
        return wrapper

    def add_entry_prompt(func):
        @wraps(func)
        def method(self, records):
            input(func.__doc__)
            menu_input = {}
            menu_input["name"] = self.view.name_menu.run()
            menu_input["minutes"] = self.view.minutes_menu.run()
            menu_input["notes"] = self.view.notes_menu.run()
            menu_input["date"] = datetime.now().date()
            return func(self, records, **menu_input)
        return method

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
