import boto3
from internal.database_dynamo import get_db
from .models import *

def insert_courses():
    db = get_db()
    table = db.Table('Courses')
    items = [
        Course(course_id='CPSC 449', name='Backend Engineering', department='Computer Science').model_dump(),
        Course(course_id='ENGL 101', name='Beginning College Writing', department='English, Comparative Literature, and Linguistics').model_dump(),
        Course(course_id='JAPN 101', name='Fundamental Japanese I', department='Modern Languages and Literatures').model_dump(),
    ]
    insert_items_into_table(table, items)

def insert_sections():
    pass

def insert_enrollments(): # make it correspond to redis' test data
    pass

def insert_items_into_table(table, items):
    for item in items:
        table.put_item(Item = item)

if __name__ == '__main__':
    insert_courses()