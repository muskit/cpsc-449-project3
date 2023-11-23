import boto3

# Create the DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Create the Sections table
table = dynamodb.create_table(
    TableName = 'Sections',
    KeySchema=[
        {'AttributeName': 'section_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'section_id', 'AttributeType': 'N'}
    ],
    ProvisionedThroughput= {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
table.wait_until_exists()

class Section:
    section_id: int
    classroom: str
    capacity: int
    waitlist_capacity: int
    day: str
    begin_time: str
    end_time: str
    instructor_id: str
    freeze: bool
    deleted: bool


# Create the Courses table
table = dynamodb.create_table(
    TableName = 'Courses',
    KeySchema=[
        {'AttributeName': 'course_code', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'course_code', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
)

# Wait for the table to be created
table.wait_until_exists()

class Course:
    course_code: str
    course_name: str

# populate dynamo table
table.put_item(
    Course = Course('Computer Science', 'CPSC449', 'Web Backend Engineering').__dict__
)

# Create the Enrollment table
table = dynamodb.create_table(
    TableName = 'Enrollment',
    KeySchema=[
        {'AttributeName': 'section_id', 'KeyType': 'HASH'},
        {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'section_id', 'AttributeType':'N'},
        {'AttributeName': 'user_id', 'AttributeType': 'N'}
    ],
    ProvisionedThroughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
)

# Wait for the table to be created
table.wait_until_exists()

class enrollment:
    section_id: int
    user_id: int
    status: str
    date: str
