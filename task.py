from peewee import *
import datetime

db = SqliteDatabase('tasks.db')
# ['name', 'minutes', 'notes', 'date']


class Task(Model):
    name = CharField(max_length=255, unique=True)
    worker = CharField(max_length=255)
    minutes = IntegerField(default=10)
    notes = TextField()
    date = DateTimeField(default=datetime.date.today)

    class Meta:
        database = db

tasks = [
    {"worker": "Nic", "name": "clean room", "minutes": 30,
    "notes": "Make sure not to miss the corners. Cleanliness is godliness"},
    {"worker": "Nic", "name": "work", "minutes": 360,
    "notes": "I love my job!"},
    {"worker": "Nic", "name": "karaoke", "minutes": 120,
    "notes": "It's a hard job, but somebody has to do it."},
    {"worker": "Tonia", "name": "jogging", "minutes": 5,
    "notes": "Fuck this."},
    {"worker": "Bob", "name": "bake bread", "minutes": 90,
    "notes": "Takes so long but smells so good. Some like it hot!"}
]

def add_tasks(tasks):
    for task in tasks:
        try:
            Task.create(**task)
        except IntegrityError:
            update = False
            task_record = Task.get(name=task["name"])
            for key, value in task.items():
                if not value == getattr(task_record, key):
                    print("This is it!")
                    setattr(task_record, key, value)
                    update = True
            if update:
                task_record.save()

def top_duration():
    task = Task.select().order_by(Task.minutes.desc()).get()
    return task

def write_record(**kwargs):
    try:
        Task.create(**task)
    except IntegrityError:
        update = False
        task_record = Task.get(name=task.get("name"))
        for key, value in task.items():
            if not value == getattr(task_record, key):
                print("This is it!")
                setattr(task_record, key, value)
                update = True
        if update:
            task_record.save()

def initialize():
    db.connect()
    db.create_tables([Task], safe=True)

# def read_records():
#     records = []
#     tasks = Task.select().order_by(Task.name.desc())
#     for key in User._meta.get_field_names():
#         print(getattr()

if __name__ == "__main__":
    initialize()
    add_tasks(tasks)
    print("the longest task is {0.name}".format(top_duration()))
    # read_records()
