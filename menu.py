import re
import subprocess


class TextMenu:
    line = "=" * 30 + "\n"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, **kwargs):
        return self.run(**kwargs)

    def clear_screen(self):
        print("\033c", end="")

    def display_items(self):
        if self.items.__class__.__name__ in ['dict']:
            for key, item in enumerate(self.items):
                print("{}) {}".format(key, item).rjust(2, " "))
        elif hasattr(self, "items") and self.items is not None:
            print(self.items)
        print("")

    def get_line(self):
        rows, columns = subprocess.check_output(
                                   ['stty', 'size']).decode().split()
        return int(columns) - 2

    def get_header(self):
        line_char = "-"
        batch_message = self.message.replace("menuline",
                                             (self.get_line() * line_char)
                                             ).strip()
        message_lines = batch_message.split('\n')
        header = "+" + (self.get_line() * line_char) + "+"
        for index, line in enumerate(message_lines):
            spaces = self.get_line() - len(line)
            padding = (spaces) * " "
            line = "|" + line + padding + "|"
            header += line
        header += "+" + (self.get_line() * line_char) + "+\n"
        return header

    def display_menu(self):
        self.clear_screen()
        print(self.get_header())
        if hasattr(self, "items"):
            self.display_items()

    def validate(self, raw, **kwargs):
        clean_input = re.search(self.regex, raw)
        try:
            if clean_input:
                return clean_input.group()
            else:
                raise ValueError("{} is not valid input".format(raw))
        except ValueError as e:
            raise e

    def input(self, **kwargs):
        raw = input("> ").lower().strip()
        return self.validate(raw, **kwargs)

    def run(self, **kwargs):
        while True:
            self.display_menu()
            try:
                choice = self.input(**kwargs)
            except ValueError as e:
                input("\n{}".format(e))
            else:
                self.items = choice if not hasattr(self, "items") else self.items
                return choice, self.items


class DictMenu(TextMenu):
    def validate(self, raw, **kwargs):
        clean = super().validate(raw, **kwargs)
        if clean not in self.items:
            raise ValueError("{} is not a valid key".format(clean))
        else:
            return clean

    def display_items(self):
        if hasattr(self, "main") and getattr(self, "main") is True:
            for key, value in self.items.items():
                choice = value.__name__.replace('_', ' ')
                print("{}) {}".format(key, choice))
        else:
            for index, item in enumerate(self.items):
                print("{}) {}".format(index + 1, item).rjust(2, " "))
        print("")

    def run(self, **kwargs):
        choice, self.items = super().run(**kwargs)
        return str(choice), self.items


class ArrayMenu(TextMenu):
    def validate(self, raw, **kwargs):
        clean = super().validate(raw, **kwargs)
        try:
            index = int(raw)
        except ValueError as e:
            raise ValueError("Expected number input, received {}".format(raw))
        else:
            if index not in list(range(1, len(self.items) + 1)):
                raise ValueError("{} is not within range".format(index))
            else:
                return index

    def display_items(self):
        for index, item in enumerate(self.items):
            print("{}) {}".format(index + 1, item[self.items_key]).rjust(2, " "))
        print("")

    def run(self, **kwargs):
        choice, self.items = super().run(**kwargs)
        return int(choice - 1), self.items
