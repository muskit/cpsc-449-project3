import boto3

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')


course_data = [
    {
        'course_id': 'CS101',
        'course_name': 'Introduction to Computer Science',
        'department': 'Computer Science'
    },
    {
        'course_id': 'CS102',
        'course_name': 'Data Structures and Algorithms',
        'department': 'Computer Science'
    },
    {
        'course_id': 'M102',
        'course_name': 'Discrete Math',
        'department': 'Mathematics'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 7,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 8,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 9,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 7,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 8,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 9,
        'status': 'enrolled',
        'date': '08/23/23'
    },   
    {
        'course_id': 'CS101',
        'course_name': 'Introduction to Computer Science',
        'department': 'Computer Science'
    },
    {
        'course_id': 'CS102',
        'course_name': 'Data Structures and Algorithms',
        'department': 'Computer Science'
    },
    {
        'course_id': 'M102',
        'course_name': 'Discrete Math',
        'department': 'Mathematics'
    }
]

enrollment_data = [
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 7,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 8,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'student_id': 9,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 7,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 8,
        'status': 'enrolled',
        'date': '08/23/23'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'student_id': 9,
        'status': 'enrolled',
        'date': '08/23/23'
    }   
]

section_data = [
    {
        'course_id': 'CS101',
        'section_id': 11114,
        'course_name': 'Introduction to Computer Science',
        'instructor_id': 1,
        'department': 'Computer Science',
        'classroom': 'CS101',
        'capacity': 30,
        'waitlist_capacity': 15,
        'days': 'Monday',
        'begin_time': '9:00 AM',
        'end_time': '10:30 AM'
    },
    {
        'course_id': 'CS102',
        'section_id': 11116,
        'course_name': 'Data Structures and Algorithms',
        'instructor_id': 3,
        'department': 'Computer Science',
        'classroom': 'CS102',
        'capacity': 20,
        'waitlist_capacity': 15,
        'days': 'Wednesday',
        'begin_time': '10:30 AM',
        'end_time': '12:00 PM'
    },
    {
        'course_id': 'M102',
        'section_id': 11115,
        'course_name': 'Discrete Math',
        'instructor_id': 3,
        'department': 'Math',
        'classroom': 'MH102',
        'capacity': 20,
        'waitlist_capacity': 15,
        'days': 'Thursday',
        'begin_time': '10:30 AM',
        'end_time': '12:00 PM'
    }
]

# Put the test data into the table
table = dynamodb.Table('Courses')
for item in course_data:
    table.put_item(Item = item)

table = dynamodb.Table('Sections')
for item in section_data:
    table.put_item(Item = item)

table = dynamodb.Table('Enrollment')
for item in enrollment_data:
    table.put_item(Item = item)

