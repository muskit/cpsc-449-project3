import boto3
import time

# custom function to wait while Global Secodary indexes are created
def wait_for_gsi(table, index_name):
    while True:
        response = table.meta.client.describe_table(TableName='EnrollmentService')
        gsi = next((i for i in response['Table'].get('GlobalSecondaryIndexes', []) if i['IndexName'] == index_name), None)
        
        if gsi and gsi['IndexStatus'] == 'ACTIVE':
            break
        
        time.sleep(3)  # Wait for 3 seconds before checking again

# Create the DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url = 'http://localhost:8000')

# Create the Sections table
table = dynamodb.create_table(
    TableName = 'EnrollmentService',
    KeySchema=[
        {'AttributeName': 'course_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'}
 
    ],
    ProvisionedThroughput= {
    'ReadCapacityUnits': 10,
    'WriteCapacityUnits': 10
    }
)

# Wait for the table to be created
table.wait_until_exists()

# Get a reference to the table
#table = dynamodb.Table('EnrollmentService')

# Add new attributes to the table
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'},
        {'AttributeName': 'section_id', 'AttributeType': 'N'},
        {'AttributeName': 'course_name', 'AttributeType': 'S'},
        {'AttributeName': 'instructor_id', 'AttributeType': 'N'},
        {'AttributeName': 'department', 'AttributeType': 'S'},
        {'AttributeName': 'classroom', 'AttributeType': 'S'},
        {'AttributeName': 'capacity', 'AttributeType': 'N'},
        {'AttributeName': 'waitlist_capacity', 'AttributeType': 'N'},
        {'AttributeName': 'days', 'AttributeType': 'S'},
        {'AttributeName': 'begin_time', 'AttributeType': 'S'},
        {'AttributeName': 'end_time', 'AttributeType': 'S'},
        {'AttributeName': 'freeze', 'AttributeType': 'N'}, 
        {'AttributeName': 'deleted', 'AttributeType': 'N'},
        {'AttributeName': 'student_id', 'AttributeType': 'N'},
        {'AttributeName': 'status', 'AttributeType': 'S'},
        {'AttributeName': 'date', 'AttributeType': 'S'}    
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 20
    }
)


# Add a global secondary index to the table
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_name', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': 'course_name_index',
                'KeySchema': [
                    {'AttributeName': 'course_name', 'KeyType': 'HASH'},
                ],
                'Projection': {
                    'ProjectionType': 'INCLUDE',
                    'NonKeyAttributes': [ 'course_name', 'department']
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        }
    ]
)


# Wait for the updates to be applied
wait_for_gsi(table, 'course_name_index')

# Add the second global secondary index
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'course_id', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': 'course_id_index',
                'KeySchema': [
                    {'AttributeName': 'course_id', 'KeyType': 'HASH'},
                ],
                'Projection': {
                    'ProjectionType': 'INCLUDE',
                    'NonKeyAttributes': ['course_name', 'department', 'classroom', 'capacity', 'waitlist_capacity', 'days', 'begin_time', 'end_time', 'instructor_id']
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        }
    ]
)

# Wait for the updates to be applied
wait_for_gsi(table, 'course_id_index')

# Add the second global secondary index
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'section_id', 'AttributeType': 'N'}
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': 'section_id_index',
                'KeySchema': [
                    {'AttributeName': 'section_id', 'KeyType': 'HASH'},
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        }
    ]
)

# Wait for the updates to be applied
wait_for_gsi(table, 'section_id_index')

# Add the second global secondary index
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'instructor_id', 'AttributeType': 'N'}
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': 'instructor_id_index',
                'KeySchema': [
                    {'AttributeName': 'instructor_id', 'KeyType': 'HASH'},
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        }
    ]
)

# Wait for the updates to be applied
wait_for_gsi(table, 'instructor_id_index')


# Add the second global secondary index
response = table.update(
    AttributeDefinitions=[
        {'AttributeName': 'student_id', 'AttributeType': 'N'}
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create': {
                'IndexName': 'student_id_index',
                'KeySchema': [
                    {'AttributeName': 'student_id', 'KeyType': 'HASH'},
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        }
    ]
)

# Wait for the updates to be applied
wait_for_gsi(table, 'student_id_index')




'''
class SectionSectionsEnrollments:
    course_code: str
    section_id: int
    course_name: str
    classroom: str
    capacity: int
    waitlist_capacity: int
    day: str
    begin_time: str
    end_time: str
    instructor_id: str
    freeze: bool
    deleted: bool
    user_id: int
    status: str
    date: str
'''

