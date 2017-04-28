import menu_strings
import inspect
import re
from math import ceil
from functools import partial, wraps, update_wrapper
from collections import OrderedDict
from datetime import datetime
from menu import Menu, NumberMenu, ItemMenu, OptionMenu


class DocView:

    menus = {
        "main": OptionMenu,
        "options": OptionMenu,
        "text": Menu,
        "key": ItemMenu,
        "name": Menu,
        "notes": Menu,
        "minutes": NumberMenu
    }

    def __init__(self, cont):
        self.main_menu = {}
        self.main_menu["options"] = OrderedDict()
        self.main_menu["message"] = cont.__class__.__doc__
        for name, func in inspect.getmembers(cont, predicate=inspect.ismethod):
            if name[-6:] == "option":
                self.main_menu["options"][name[0]] = func
        self.main_menu = self.menus["main"](**self.main_menu)

    def main_prompt(func):
        def method(self, *args, **kwargs):
            records = func(self, *args, **kwargs)
            prompt = self.view.main_menu()
            item = prompt(records)
            self.view.print_item(item)
        return method

    def get_message_text(self, func, pos):
        messages = []
        regex = r"\*{pos}\*(?P<message>[\w\s.\n\'\-/:]+)\*{pos}\*".format(pos=pos)
        message_pattern = re.compile(regex, re.X | re.M)
        for match in message_pattern.finditer(func.__doc__):
            messages.append(match.groupdict())
        return messages

    def pre_prompt(menu_type):
        def wrapper(func, *args, **kwargs):
            @wraps(func)
            def method(self, *args_two, **kwargs_two):
                Prompt = self.view.menus[menu_type]
                message = self.view.get_message_text(func, menu_type)[0]  # fix
                prompt = Prompt(**message)
                kwargs_two[menu_type] = prompt()
                return func(self, *args_two, **kwargs_two)
            return method
        return wrapper

    def post_prompt(menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, *args, **kwargs):
                items = func(self, *args, **kwargs)
                messages = self.view.get_message_text(func, menu_type)
                message = {
                    "message": messages[0]["message"],
                    "second_message": messages[1]["message"]}
                PromptWithoutMessage = self.view.menus[menu_type]
                Prompt = partial(PromptWithoutMessage, **message)
                items_prompt = Prompt(items=items, items_key="name")
                item = items_prompt()
                return item
            return method
        return wrapper

    def print_item(self, task):
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
