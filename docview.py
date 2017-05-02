import re
import sys
from functools import partial, wraps, update_wrapper
from collections import OrderedDict
from menu import TextMenu, DictMenu, ArrayMenu


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
        self.main_options["regex"] = r"[\w]"
        self.main_options[options] = {}  # OrderedDict()
        self.main_options["message"] = cont.__class__.__doc__
        for name in dir(cont):
            if not name[:2] == "__" and self.is_docview(cont, name):
                self.main_options[options][name[0]] = getattr(cont, name)
        quit = self.quit if not hasattr(kwargs, "quit") else kwargs["quit"]
        self.main_options[options]["q"] = quit
        self.print_item = cont.print_item

    def is_docview(self, cont, method):
        doc_exists = getattr(cont, method).__doc__
        return doc_exists and doc_exists[:7] == "DocView"

    def get_message_text(self, func, pos):
        regex = r"\*{pos}\*(?P<message>[\w\s.\n\'\-/:/?]+)\*{pos}\*".format(
                                                                    pos=pos)
        message_pattern = re.compile(regex, re.X | re.M)
        message = message_pattern.search(func.__doc__)["message"]
        return message

    def normalize_items(self, items_type=None, records=None, menu_input=None):
        if items_type == 'text':
            return None
        else:
            if len(menu_input.keys()) == 0:
                return records
            else:
                keys = list(menu_input)
                return menu_input[keys[len(keys) - 1]]

    def get_menu_config(self, menu_type):
        menu_config = menu_type.split(":")
        if len(menu_config) == 2:
            menu_config.append("name")
        return menu_config

    def configure_menu(self, func, menu_config, items=None, regex=None):
        items_type, field_name, display_key = menu_config
        message = self.get_message_text(func, field_name)
        Prompt = self.menus[items_type]
        return Prompt(items=items, items_key=display_key, message=message,
                      regex=regex)

    def process_input(self, items_type=None, items=None, choice=None):
        return items[choice] if items_type not in ['text', 'edit'] else choice

    def main_prompt(func):
        def method(self, *args, **kwargs):
            records = func(self, *args, **kwargs)
            Prompt = DictMenu(**self.view.main_options)
            choice, prompts = Prompt()
            chosen_func = prompts[choice]
            choice, item = chosen_func(records)
            if not item == 'q':
                self.view.print_item(item)
        return method

    def pre_prompt(regex, menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records, **menu_input):
                menu_config = self.view.get_menu_config(menu_type)
                items_type, field_name, display_key = menu_config

                items = self.view.normalize_items(items_type=items_type,
                                                  records=records,
                                                  menu_input=menu_input)

                prompt = self.view.configure_menu(func, menu_config,
                                                  items=items, regex=regex)

                choice, items_to_filter = prompt()

                new_input = self.view.process_input(items_type=items_type,
                                                    items=items_to_filter,
                                                    choice=choice)

                menu_input.update({field_name: new_input})

                return choice, func(self, records, **menu_input)
            return method
        return wrapper

    def post_prompt(regex, menu_type):
        def wrapper(func):
            @wraps(func)
            def method(self, records, **menu_input):
                choice, items = func(self, records)

                menu_config = self.view.get_menu_config(menu_type)

                prompt = self.view.configure_menu(func, menu_config,
                                                  items=items, regex=regex)

                choice, item = prompt()

                return choice, item[choice]
            return method
        return wrapper

    def unpack_results(self, *task):
        while task.__class__.__name__ == 'tuple':
            toss, task = task
        return task

    def quit(self, records):
        return sys.exit()
