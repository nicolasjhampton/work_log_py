#!/usr/bin/env python3

import sys
import re

from datetime import datetime, timedelta

from view import View
from csv_interface import CSVInterface


class WorkLog:
    """Welcome to the work log!
What would you like to do?
menuline
"""

    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.view = kwargs.get("View")(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def run(self):
        while True:
            records = self.model.read_records()
            func = self.view.main_menu_prompt()
            task = func(records)
            self.view.print_task(task)

    @View.add_entry_prompt
    def add_entry_option(self, records, **menu_input):
        """add an entry"""
        self.model.write_record(**menu_input)
        input("Record written!")
        return task

    @View.post_prompt("key")
    def date_search_option(self, records, **menu_input):
        """find an entry by date"""
        tasks = self.gen_keys("date", records)
        return tasks

    @View.post_prompt("key")
    def search_by_duration_option(self, records, **menu_input):
        """find an entry by task duration"""
        tasks = self.gen_keys("minutes", records)
        return tasks

    @View.post_prompt("key")
    @View.pre_prompt("text")
    def match_entry_option(self, records, **menu_input):
        """match a phrase or pattern"""
        tasks = self.match_entries(records, menu_input["phrase"])
        return tasks

    def x_quit_option(self, records):
        """exit the program"""
        sys.exit()

    def match_entries(self, records, phrase):
        matches = []
        line = re.compile(phrase, re.I)
        for row in records:
            name = row["name"]
            notes = row["notes"]
            if re.search(line, name) or re.search(line, notes):
                matches.append(row)
        tasks = self.gen_keys("date", matches)
        return tasks

    def gen_keys(self, target_key, records):
        tasks = {}
        for row in records:
            key = str(row[target_key])
            try:
                tasks[key]
            except:
                tasks[key] = []
            tasks[key].append(row)
        return tasks


if __name__ == "__main__":
    file_settings = {
        "fieldnames": ['name', 'minutes', 'notes', 'date'],
        "filename": "work_log.csv"
    }
    work_log = WorkLog(model=CSVInterface(**file_settings), View=View)
    work_log.run()
