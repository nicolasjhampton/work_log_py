import csv


class CSVInterface:
    def __init__(self, **kwargs):
        self.filename = kwargs.get("filename")
        self.fieldnames = kwargs.get("fieldnames")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def write_record(self, **kwargs):
        with open(self.filename, "a") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(kwargs)

    def read_records(self):
        records = []
        with open(self.filename) as file:
            reader = csv.DictReader(file, fieldnames=self.fieldnames)
            for row in reader:
                records.append(dict(row))
        return records
