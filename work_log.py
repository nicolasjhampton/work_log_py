#!/usr/bin/env python3

import sys
import re

from math import ceil
from datetime import datetime

from docview import DocView
from csv_interface import CSVInterface


class WorkLog:
    """Welcome to the work log!
What would you like to do?"""

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
        try:
            records = self.model.read_records()
        except IOError:
            input("Read/Write error!")
        return records

    @DocView.pre_prompt(r"([\w\s]+)", "text:name")
    @DocView.pre_prompt(r"([\d]+)", "text:minutes")
    @DocView.pre_prompt(r"([\w\d\s.,\?\!:\-]+)", "text:notes")
    def add_entry(self, records, **menu_input):
        """DocView
        *notes*Please enter any notes related to this task*notes*
        *minutes*Please enter total minutes spent on task*minutes*
        *name*Please enter a name for the task*name*"""
        menu_input["date"] = datetime.now().date()
        task = menu_input
        try:
            self.model.write_record(**task)
        except IOError:
            input("Read/Write error!")
        input("Record written!")
        return None, task

    @DocView.pre_prompt(r"([\w\s]+)", "array:item")
    def delete_entry(self, records, **menu_input):
        """DocView
        *item*Now enter an item index:*item*"""
        task = menu_input["item"]
        records.remove(task)
        try:
            self.model.save_records(records)
        except IOError:
            input("Read/Write error!")
        input("Record removed!")
        return None, task

    @DocView.pre_prompt(r"([\w\s]+)", "array:index")
    @DocView.pre_prompt(r"([\w]+)", "dict:item")
    @DocView.pre_prompt(r"([\w\d\s.,\?\!:\-]+)", "edit:edit")
    def edit_entry(self, records, **menu_input):
        """DocView
        *index*Enter an item index:*index*
        *item*What field would you like to edit?*item*
        *edit*Please enter new value*edit*"""
        taskIndex = records.index(menu_input["index"])
        task = records.pop(taskIndex)
        for key, value in task.items():
            if value == menu_input['item']:
                search_key = key
        menu_input["index"][search_key] = menu_input["edit"]
        records.insert(taskIndex, task)
        try:
            self.model.save_records(records)
        except IOError:
            input("Read/Write error!")
        input("Record edited!")
        return None, task

    @DocView.post_prompt(r"([\d]+)", "array:item")
    @DocView.post_prompt(r"([\d]{4}-[\d]{2}-[\d]{2})", "dict:date")
    def time_search(self, records, **menu_input):
        """DocView
        *date*Please enter a date key:*date*
        *item*Now enter an item index:*item*"""
        tasks = self.gen_keys("date", records)
        return None, tasks

    @DocView.post_prompt(r"([\d]+)", "array:item")
    @DocView.post_prompt(r"([\d]+)", "dict:minutes")
    def search_by_duration(self, records, **menu_input):
        """DocView
        *minutes*Please enter a minutes key:*minutes*
        *item*Now enter an item index:*item*"""
        tasks = self.gen_keys("minutes", records)
        return None, tasks

    @DocView.post_prompt(r"([\d]+)", "array:item")
    @DocView.post_prompt(r"([\d]{4}-[\d]{2}-[\d]{2})", "dict:date")
    @DocView.pre_prompt(r"([\w\d\s.\?\!:\-]+)", "text:text")
    def match_entry(self, records, **menu_input):
        """DocView
        *text*Please enter a phrase/pattern:*text*
        *date*Please enter a date key:*date*
        *item*Now enter a numbered item choice:*item*"""
        tasks = self.match_entries(records, menu_input["text"])
        return tasks

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

    def print_item(self, args):
        task = self.view.unpack_results(args)
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


if __name__ == "__main__":
    file_settings = {
        "fieldnames": ['name', 'minutes', 'notes', 'date'],
        "filename": "work_log.csv"
    }
    work_log = WorkLog(model=CSVInterface(**file_settings), View=DocView)
    work_log()
