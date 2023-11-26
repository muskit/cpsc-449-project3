import boto3
from internal.database_dynamo import get_db
from .models import *

def insert_items_into_table(table, items):
    for item in items:
        table.put_item(Item = item)

def insert_courses():
    db = get_db()
    table = db.Table('Courses')
    items = [
        Course(course_id='CPSC 449', course_name='Backend Engineering', department='Computer Science').model_dump(),
        Course(course_id='ENGL 101', course_name='Beginning College Writing', department='English, Comparative Literature, and Linguistics').model_dump(),
        Course(course_id='JAPN 101', course_name='Fundamental Japanese I', department='Modern Languages and Literatures').model_dump(),
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
        ).model_dump(),
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
        ).model_dump(),
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
        ).model_dump(),
        Section(
            section_id=11211,
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
        ).model_dump(),
    ]
    insert_items_into_table(table, items)

def insert_enrollments(): # make it correspond to redis' test data
    db = get_db()
    table = db.Table('Enrollments')
    items = [
        Enrollment(
            student_id=1,
            section_id=11310,
            enrollment_status=EnrollmentStatus.ENROLLED
        ).model_dump(),
        Enrollment(
            student_id=5,
            section_id=11011,
            enrollment_status=EnrollmentStatus.ENROLLED
        ).model_dump(),
        Enrollment(
            student_id=7,
            section_id=11312,
            enrollment_status=EnrollmentStatus.ENROLLED
        ).model_dump(),
    ]
    insert_items_into_table(table, items)

if __name__ == '__main__':
    insert_courses()
    insert_sections()
    insert_enrollments()