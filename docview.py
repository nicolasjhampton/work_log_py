import re
from math import ceil
from functools import partial, wraps, update_wrapper
from collections import OrderedDict
from menu import Menu, ItemMenu, OptionMenu, IndexMenu


class DocView:

    menus = {
        "main": OptionMenu,
        "options": OptionMenu,
        "text": Menu,
        "key": ItemMenu,
        "name": Menu,
        "notes": Menu,
        "minutes": ItemMenu,
        "date": ItemMenu,
        "index": IndexMenu
    }

    def __init__(self, cont):
        self.main_menu = {}
        self.main_menu["options"] = OrderedDict()
        self.main_menu["message"] = cont.__class__.__doc__
        for name in dir(cont):
            if not name[:2] == "__" and self.is_docview(cont, name):
                self.main_menu["options"][name[0]] = getattr(cont, name)
        self.main_menu = self.menus["main"](**self.main_menu)

    def is_docview(self, cont, method):
        doc_exists = getattr(cont, method).__doc__
        return doc_exists and doc_exists[:7] == "DocView"

    def main_prompt(func):
        def method(self, *args, **kwargs):
            records = func(self, *args, **kwargs)
            prompt = self.view.main_menu(regex=r"[\w]")
            item = prompt(records)
            self.view.print_item(item)
        return method

    def get_message_text(self, func, pos):
        messages = []
        regex = r"\*{pos}\*(?P<message>[\w\s.\n\'\-/:]+)\*{pos}\*".format(pos=pos)
        message_pattern = re.compile(regex, re.X | re.M)
        message = message_pattern.search(func.__doc__)["message"]
        return message

    def pre_prompt(regex, menu_type):
        def wrapper(func, *args, **kwargs):
            @wraps(func)
            def method(self, *args_two, **kwargs_two):
                message = self.view.get_message_text(func, menu_type)
                PromptWithoutMessage = self.view.menus[menu_type]
                prompt = PromptWithoutMessage(message=message)
                kwargs_two[menu_type] = prompt(regex=regex)
                return func(self, *args_two, **kwargs_two)
            return method
        return wrapper

    def post_prompt(regex, menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, *args, **kwargs):
                items = func(self, *args, **kwargs)
                message = self.view.get_message_text(func, menu_type)
                PromptWithoutMessage = self.view.menus[menu_type]
                Prompt = partial(PromptWithoutMessage, message=message)
                input(items)
                items_prompt = Prompt(items=items, items_key="name")
                item = items_prompt(regex=regex)
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
