import sys
import re

from datetime import datetime, timedelta

from view import View
from csv_interface import CSVInterface


class WorkLog:
    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.view = kwargs.get("view")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def run(self):
        while True:
            records = self.model.read_records()
            choice = self.view.main_menu_prompt()
            if choice == "add entry":
                task = self.add_entry()
            elif choice == "look up entry":
                task = self.find_entry(records)
            elif choice == "find matching phrase or pattern":
                task = self.match_entry(records)
            elif choice == "quit work log":
                sys.exit()
            self.view.print_task(task)

    def add_entry(self):
        name, minutes, notes = self.view.add_entry_prompt()
        task = {
            "name": name,
            "minutes": minutes,
            "notes": notes,
            "date": datetime.now().date()
        }
        self.model.write_record(**task)
        input("Record written!")
        return task

    def find_entry(self, records):
        method = self.view.find_prompt()
        if method == "date":
            tasks = self.gen_keys("date", records)
        elif method == "task duration":
            tasks = self.gen_keys("minutes", records)
        task = self.view.task_prompt(tasks)
        return task

    def match_entry(self, records):
        phrase = self.view.match_prompt()
        tasks = self.match_entries(records, phrase)
        task = self.view.task_prompt(tasks)
        return task

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
    work_log = WorkLog(model=CSVInterface(**file_settings), view=View())
    work_log.run()
