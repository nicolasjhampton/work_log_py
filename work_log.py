#!/usr/bin/env python3

import sys
import re

from datetime import datetime, timedelta

from docview import DocView
from csv_interface import CSVInterface


class WorkLog:
    """Welcome to the work log!
What would you like to do?
menuline
"""

    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.View = kwargs.get("View")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self):
        self.view = self.View(self)
        while True:
            self.run()

    @DocView.main_prompt
    def run(self):
        return self.model.read_records()

    @DocView.pre_prompt("name")
    @DocView.pre_prompt("minutes")
    @DocView.pre_prompt("notes")
    def add_entry(self, records, **menu_input):
        """DocView
        *notes*Please enter any notes related to this task\nmenuline*notes*
        *minutes*Please enter total minutes spent on task\nmenuline*minutes*
        *name*Please enter a name for the task\nmenuline*name*"""
        menu_input["date"] = datetime.now().date()
        self.model.write_record(**menu_input)
        input("Record written!")
        return menu_input

    @DocView.post_prompt("index")
    @DocView.post_prompt("date")
    def date_search(self, records, **menu_input):
        """DocView
        *date*Please enter a date key:\nmenuline*date*
        *index*Now enter an item index:*index*"""
        tasks = self.gen_keys("date", records)
        return tasks

    @DocView.post_prompt("index")
    @DocView.post_prompt("date")
    def search_by_duration(self, records, **menu_input):
        """DocView
        *date*Please enter a minutes key:\nmenuline*date*
        *index*Now enter an item index:*index*"""
        tasks = self.gen_keys("minutes", records)
        return tasks


    @DocView.pre_prompt("text")
    @DocView.post_prompt("index")
    @DocView.post_prompt("date")
    def match_entry(self, records, **menu_input):
        """DocView
        *text*Please enter a phrase/pattern:\nmenuline*text*
        *date*Please enter a date key:\nmenuline*date*
        *index*Now enter a numbered item choice:*index*"""
        tasks = self.match_entries(records, menu_input["text"])
        return tasks

    def x_exit_the_program(self, records):
        """DocView exit the program"""
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
    work_log = WorkLog(model=CSVInterface(**file_settings), View=DocView)
    work_log()
