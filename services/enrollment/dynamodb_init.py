import boto3
import time

'''# custom function to wait while Global Secodary indexes are created
def wait_for_update(table, index_name):
    while True:
        response = table.meta.client.describe_table(TableName='EnrollmentService')
        gsi = next((i for i in response['Table'].get('GlobalSecondaryIndexes', []) if i['IndexName'] == index_name), None)
        
        if gsi and gsi['IndexStatus'] == 'ACTIVE':
            break
        
        time.sleep(3)  # Wait for 3 seconds before checking again
'''

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

response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'},
        {'AttributeName': 'section_id', 'AttributeType': 'N'},
        {'AttributeName': 'course_name', 'AttributeType': 'S'},
        {'AttributeName': 'instructor_id', 'AttributeType': 'N'},
        {'AttributeName': 'classroom', 'AttributeType': 'S'},
        {'AttributeName': 'capacity', 'AttributeType': 'N'},
        {'AttributeName': 'waitlist_capacity', 'AttributeType': 'N'},
        {'AttributeName': 'current_capacity', 'AttributeType': 'N'},
        {'AttributeName': 'days', 'AttributeType': 'S'},
        {'AttributeName': 'begin_time', 'AttributeType': 'S'},
        {'AttributeName': 'end_time', 'AttributeType': 'S'},
        {'AttributeName': 'freeze', 'AttributeType': 'N'}, 
        {'AttributeName': 'deleted', 'AttributeType': 'N'}   
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 15
    }
)


# Create the Courses table
table = dynamodb.create_table(
    TableName = 'Courses',
    KeySchema=[
        {'AttributeName': 'course_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'}
    ],
    ProvisionedThroughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
table.wait_until_exists()

response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'},
        {'AttributeName': 'course_name', 'AttributeType': 'S'},
        {'AttributeName': 'department', 'AttributeType': 'S'}  
    ],
    ProvisionedThroughput = {
    'ReadCapacityUnits': 6,
    'WriteCapacityUnits': 6
    }
)

# Create the Enrollment table
table = dynamodb.create_table(
    TableName = 'Enrollment',
    KeySchema=[
        {'AttributeName': 'section_id', 'KeyType': 'HASH'},
        {'AttributeName': 'student_id', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'section_id', 'AttributeType':'N'},
        {'AttributeName': 'student_id', 'AttributeType': 'N'}
    ],
    ProvisionedThroughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
table.wait_until_exists()

# Add new attributes to the table
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'},
        {'AttributeName': 'section_id', 'AttributeType': 'N'},
        {'AttributeName': 'student_id', 'AttributeType': 'N'},
        {'AttributeName': 'status', 'AttributeType': 'S'},
        {'AttributeName': 'date', 'AttributeType': 'S'}    
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 10
    }
)






