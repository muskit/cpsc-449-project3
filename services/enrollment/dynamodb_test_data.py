import boto3

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

table = dynamodb.Table('EnrollmentService')

# Create the test data
test_data = [
    {
        'course_id': 'CS101',
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
for item in test_data:
    table.put_item(Item = item)

