import boto3

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
'''
# Get the Sections table
table = dynamodb.Table('Sections')

# Create 10 test data entries
test_data = [
    {
        'section_id': 1,
        'classroom': 'A101',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Monday',
        'begin_time': '9:00 AM',
        'end_time': '10:00 AM',
        'instructor_id': '1',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 2,
        'classroom': 'A102',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Tuesday',
        'begin_time': '9:00 AM',
        'end_time': '10:00 AM',
        'instructor_id': '2',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 3,
        'classroom': 'A103',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Wednesday',
        'begin_time': '9:00 AM',
        'end_time': '10:00 AM',
        'instructor_id': '3',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 4,
        'classroom': 'A104',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Thursday',
        'begin_time': '9:00 AM',
        'end_time': '10:00 AM',
        'instructor_id': '4',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 5,
        'classroom': 'A105',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Friday',
        'begin_time': '9:00 AM',
        'end_time': '10:00 AM',
        'instructor_id': '5',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 6,
        'classroom': 'B101',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Monday',
        'begin_time': '10:00 AM',
        'end_time': '11:00 AM',
        'instructor_id': '6',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 7,
        'classroom': 'B102',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Tuesday',
        'begin_time': '10:00 AM',
        'end_time': '11:00 AM',
        'instructor_id': '7',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 8,
        'classroom': 'B103',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Wednesday',
        'begin_time': '10:00 AM',
        'end_time': '11:00 AM',
        'instructor_id': '8',
        'freeze': False,
        'deleted': False
    },
    {
        'section_id': 9,
        'classroom': 'B104',
        'capacity': 30,
        'waitlist_capacity': 10,
        'day': 'Thursday',
        'begin_time': '10:00 AM',
        'end_time': '1:00 PM',
    }
]

# Add the test data to the table
for item in test_data:
    table.put_item(Item=item)
'''
table = dynamodb.Table('Courses')

test_data = [
    {
        'course_code': 'CPSC449',
        'course_name': 'Web backend engineering'
    },
    {
        'course_code': 'CPSC349',
        'course_name': 'Web front-end engineering'
    },
    {
        'course_code': 'CPSC101',
        'course_name': 'Intro to Computer Sciencee'
    },
    {
        'course_code': 'M200',
        'course_name': 'Algebra 1'
    },
]

for item in test_data:
    table.put_item(Item=item)


table = dynamodb.Table('Enrollment')

test_data = [
    {
        'section_id': 1,
        'user_id': 4,
        'status': 'erolled',
        'date': '08-21-23'
    },
    {
        'section_id': 1,
        'user_id': 5,
        'status': 'enrolled',
        'date': '08-21-23'
    },
    {
        'section_id': 1,
        'user_id': 6,
        'status': 'enrolled',
        'date': '08-22-23'
    },
    {
        'section_id': 2,
        'user_id': 4,
        'status': 'enrolled',
        'date': '08-23-23'
    },
]

for item in test_data:
    table.put_item(Item=item)

