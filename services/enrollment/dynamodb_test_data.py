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
    db = get_db()
    table = db.Table('Sections')
    items = [
        Section(
            section_id=11310,
            course_id='CPSC 449',
            classroom='CS 110',
            capacity=30,
            waitlist_capacity=30,
            days=['Mon'],
            begin_time='16:00',
            end_time="18:45",
            freeze=False,
            deleted=False,
            instructor_id=2
        ),
        Section(
            section_id=11312,
            course_id='CPSC 449',
            classroom='CS 110',
            capacity=30,
            waitlist_capacity=30,
            days=['Mon'],
            begin_time='19:00',
            end_time="21:45",
            freeze=False,
            deleted=False,
            instructor_id=2
        ),
        Section(
            section_id=11011,
            course_id='ENGL 101',
            classroom='SGMH 303',
            capacity=30,
            waitlist_capacity=30,
            days=['Mon', 'Wed'],
            begin_time='13:00',
            end_time="14:15",
            freeze=False,
            deleted=False,
            instructor_id=4
        ),
        Section(
            section_id=11011,
            course_id='JAPN 102',
            classroom='HUM 203',
            capacity=30,
            waitlist_capacity=30,
            days=['Mon', 'Wed'],
            begin_time='13:00',
            end_time="14:15",
            freeze=False,
            deleted=False,
            instructor_id=3
        ),
    ]
    insert_items_into_table(table, items)

def insert_enrollments(): # make it correspond to redis' test data
    pass

def insert_items_into_table(table, items):
    for item in items:
        table.put_item(Item = item)

if __name__ == '__main__':
    insert_courses()