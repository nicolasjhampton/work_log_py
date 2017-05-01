import re
import sys
from functools import partial, wraps, update_wrapper
from collections import OrderedDict
from menu import TextMenu, DictMenu, ArrayMenu
import json


class DocView:

    menus = {
        "main": DictMenu,
        "text": TextMenu,
        "dict": DictMenu,
        "array": ArrayMenu,
        "edit": TextMenu
    }

    def __init__(self, cont, **kwargs):
        options = "items"
        self.main_options = {"main": True}
        self.main_options[options] = {} #OrderedDict()
        self.main_options["message"] = cont.__class__.__doc__
        for name in dir(cont):
            if not name[:2] == "__" and self.is_docview(cont, name):
                self.main_options[options][name[0]] = getattr(cont, name)
        quit = self.quit if not hasattr(kwargs, "quit") else kwargs["quit"]
        self.main_options[options]["q"] = quit
        self.print_item = cont.print_item
        # self.main_menu = self.menus["main"](**self.main_options)

    def is_docview(self, cont, method):
        doc_exists = getattr(cont, method).__doc__
        return doc_exists and doc_exists[:7] == "DocView"

    def main_prompt(func):
        def method(self, *args, **kwargs):
            records = func(self, *args, **kwargs)
            Prompt = DictMenu(**self.view.main_options) #DictMenu
            choice, prompts = Prompt(regex=r"[\w]")
            chosen_func = prompts[choice]
            choice, item = chosen_func(records)
            if not item == 'q':
                self.view.print_item((choice,item))
        return method

    def get_message_text(self, func, pos):
        messages = []
        regex = r"\*{pos}\*(?P<message>[\w\s.\n\'\-/:/?]+)\*{pos}\*".format(pos=pos)
        message_pattern = re.compile(regex, re.X | re.M)
        message = message_pattern.search(func.__doc__)["message"]
        return message

    def pre_prompt(regex, menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records, **menu_input): # records, **menu_input
                menu_config = self.view.get_menu_config(menu_type)
                if not menu_config[0] == 'text':
                    if len(menu_input.keys()) == 0:
                        items = records #[list(menu_input.keys())[0]]
                    else:
                        keys = list(menu_input)
                        input(menu_input)
                        input(keys)
                        items = menu_input[keys[len(keys) - 1]]
                        input("items")
                else:
                    items = None
                input(items)
                prompt = self.view.configure_menu(func, menu_config, items=items, items_key=menu_config[1])
                choice, new_items = prompt(regex=regex) #
                # new_items = menu_input[menu_config[1]]
                input(choice)
                if new_items.__class__.__name__ in ['dict', 'list'] and any(new_items):
                    new_input = new_items[choice]
                else:
                    input("in")
                    new_input = choice
                menu_input.update({menu_config[1]:new_input})
                input(menu_input)
                input(func)
                return choice, func(self, records, **menu_input)
            return method
        return wrapper

    def get_menu_config(self, menu_type):
        menu_config = menu_type.split(":")
        params = len(menu_config)
        if params == 1:
            menu_config.insert(0,"text")
            return menu_config
        elif params == 2:
            menu_config.append("name")
            return menu_config
        elif params == 3:
            return menu_config

    def configure_menu(self, func, menu_config, items=None, items_key=None):
        message = self.get_message_text(func, menu_config[1])
        PromptWithoutMessage = self.menus[menu_config[0]]
        # if menu_config[0] == 'text':
        #     return PromptWithoutMessage(message=message)
        # else:
        Prompt = partial(PromptWithoutMessage, message=message)
        return Prompt(items=items, items_key=items_key)

    def post_prompt(regex, menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records, **menu_input):
                menu_config = self.view.get_menu_config(menu_type)
                choice, items = func(self, records) #, **kwargs_two)
                prompt = self.view.configure_menu(func, menu_config, items=items, items_key=choice)
                choice, item = prompt(regex=regex)
                return choice, item[choice]
            return method
        return wrapper

    def quit(self, records):
        return sys.exit()
