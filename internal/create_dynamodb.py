import boto3

# Create the Sections table
def create_table_sections(client):
    table_name = 'Sections'
    partition_key = 'section_id'
    sort_key = 'course_id'
    throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    table = client.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': partition_key, 'AttributeType': 'S'},
            {'AttributeName': sort_key, 'AttributeType': 'S'},
            {'AttributeName': 'instructor_id', 'AttributeType': 'N'},
            {'AttributeName': 'classroom', 'AttributeType': 'S'},
            {'AttributeName': 'capacity', 'AttributeType': 'N'},
            {'AttributeName': 'waitlist_capacity', 'AttributeType': 'N'},
            {'AttributeName': 'day', 'AttributeType': 'S'},
            {'AttributeName': 'begin_time', 'AttributeType': 'S'},
            {'AttributeName': 'end_time', 'AttributeType': 'S'},
            {'AttributeName': 'freeze', 'AttributeType': 'BOOL'},
            {'AttributeName': 'deleted', 'AttributeType': 'BOOL'}
        ],
        ProvisionedThroughput=throughput,
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'GSI-1',
                'KeySchema': [
                    {'AttributeName': 'course_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'section_id', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'GSI-2',
                'KeySchema': [
                    {'AttributeName': 'capacity', 'KeyType': 'HASH'},
                    {'AttributeName': 'section_id', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'GSI-3',
                'KeySchema': [
                    {'AttributeName': 'waitlist_capacity', 'KeyType': 'HASH'},
                    {'AttributeName': 'section_id', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ]
    )

    # Wait for the table to be created
    table.wait_until_exists()

# Create the Courses table
def create_table_courses(client):
    table_name = 'Courses'
    partition_key = 'course_id'
    sort_key = 'name'
    throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    table = client.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': partition_key, 'AttributeType': 'S'},
            {'AttributeName': sort_key, 'AttributeType': 'S'},
            {'AttributeName': "code", 'AttributeType': 'S'},
            {'AttributeName': "name", 'AttributeType': 'S'}
        ],
        ProvisionedThroughput=throughput
    )

    # Wait for the table to be created
    table.wait_until_exists()

# Create the Departments table
def create_table_departments(client):
    table_name = 'Departments'
    partition_key = 'department_id'
    sort_key = 'name'
    throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    table = client.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': partition_key, 'AttributeType': 'S'},
            {'AttributeName': sort_key, 'AttributeType':'S'}
        ],
        ProvisionedThroughput=throughput
    )

    # Wait for the table to be created
    table.wait_until_exists()

# Create the Enrollment table
def create_table_enrollments(client):
    table_name = 'Enrollment'
    partition_key = 'user_id'
    sort_key = 'section_id'
    throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    table = client.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': partition_key, 'AttributeType':'S'},
            {'AttributeName': sort_key, 'AttributeType': 'S'},
            {'AttributeName': "status", 'AttributeType':'S'},
            {'AttributeName': "grade", 'AttributeType':'S'},
            {'AttributeName': "date", 'AttributeType':'S'},
        ],
        ProvisionedThroughput=throughput,
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'GSI-1',
                'KeySchema': [
                    {'AttributeName': 'section_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'GSI-2',
                'KeySchema': [
                    {'AttributeName': 'status', 'KeyType': 'HASH'},
                    {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }

        ]
    )

    # Wait for the table to be created
    table.wait_until_exists()

if __name__ == '__main__':
    dynamodb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    create_table_sections(dynamodb)
    create_table_courses(dynamodb)
    create_table_departments(dynamodb)
    create_table_enrollments(dynamodb)