from peewee import *

db = SqliteDatabase('tasks.db')
# ['name', 'minutes', 'notes', 'date']

class Task(Model):
    name = CharField(max_length=255, unique=True)
    minutes = IntegerField(default=10)
    notes = CharField(max_length=255)

    class Meta:
        database = db

if __name__ == "__main__":
    db.connect()
    db.create_tables([Task], safe=True)
