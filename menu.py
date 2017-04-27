class Menu:
    line = "=" * 30 + "\n"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def clear_screen(self):
        print("\033c", end="")

    def display_menu(self):
        self.clear_screen()
        print(self.message.replace("menuline", self.line))

    def input(self):
        return input("> ").lower().strip()

    def run(self):
        self.display_menu()
        print("")
        return self.input()


class OptionMenu(Menu):
    def validate_key(self, raw):
        if raw not in self.options:
            raise ValueError("{} is not a valid key".format(raw))
        else:
            return raw

    def display_choice_menu(self):
        super().display_menu()
        for key, value in self.options.items():
            print("{}) {}".format(key, value.__doc__))
        print("")

    def run(self):
        while True:
            self.display_choice_menu()
            raw = self.input()
            try:
                choice = self.validate_key(raw)
            except ValueError as e:
                input("\n{}".format(e))
            else:
                return self.options[choice]


class NumberMenu(Menu):
    def validate_number(self, raw):
        try:
            number = int(raw)
        except ValueError:
            raise ValueError("{} is not an integer".format(raw))
        else:
            return number

    def run(self):
        while True:
            raw = super().run()
            try:
                number = self.validate_number(raw)
            except ValueError as e:
                input("\n{}".format(e))
            else:
                return number


class IndexMenu(NumberMenu, Menu):
    def validate_choice(self, raw, maxIndex):
        choice = super().validate_number(raw)
        if choice not in list(range(1, maxIndex + 1)):
            raise ValueError("{} is not within range".format(choice))
        else:
            return choice

    def display_choice_menu(self):
        super().display_menu()
        for index, option in enumerate(self.options):
            print("{}) {}".format(index + 1, option.title()))
        print("")

    def run(self):
        while True:
            self.display_choice_menu()
            raw = self.input()
            try:
                choice = self.validate_choice(raw, len(self.options))
            except ValueError as e:
                input("\n{}".format(e))
            else:
                return self.options[choice - 1]


class ItemMenu(IndexMenu, NumberMenu, Menu):
    def validate_key(self, raw):
        if raw not in self.items.keys():
            raise ValueError("{} is not a valid key".format(raw))
        else:
            return raw

    def display_item_menu(self):
        self.display_menu()
        for groupIndex, group in enumerate(self.items.items()):
            key, coll = group
            print("{}. {}:".format(groupIndex + 1, key))
            for index, item in enumerate(coll):
                print("   {}) {}".format(index + 1, item[self.key]))
        print("")

    def second_run(self):
        print(self.second_message.replace("menuline", self.line))
        print("")
        return self.input()

    def run(self):
        while True:
            self.display_item_menu()
            raw = self.input()
            try:
                key_choice = self.validate_key(raw)
            except ValueError as e:
                input("\n{}".format(e))
            else:
                raw = self.second_run()
                try:
                    value_choice = self.validate_choice(
                                            raw, len(self.items[key_choice]))
                except ValueError as e:
                    input("\n{}".format(e))
                else:
                    return self.items[key_choice][value_choice - 1]
