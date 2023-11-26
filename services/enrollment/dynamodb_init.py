from internal.database_dynamo import *
from time import sleep

### TODO: Global Secondary Indexes ##
# Sections: instructor_id

def table_create_courses(db):
    if table_exists(db, 'Courses'): return

    ## Table creation
    table = db.create_table(
        TableName = 'Courses',
        KeySchema=[
            {'AttributeName': 'course_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'course_id', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.wait_until_exists()

    ## other attributes:
    # AttributeDefinitions=[
    #     {'AttributeName': 'name', 'AttributeType': 'S'},
    #     {'AttributeName': 'department', 'AttributeType': 'S'}  
    # ]

def table_create_sections(db):
    if table_exists(db, 'Sections'): return

    table = db.create_table(
        TableName = 'Sections',
        KeySchema=[
            {'AttributeName': 'section_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'section_id', 'AttributeType': 'N'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.wait_until_exists()

	## other attributes:
    # AttributeDefinitions=[
    #     {'AttributeName': 'course_id', 'AttributeType': 'S'},
    #     {'AttributeName': 'instructor_id', 'AttributeType': 'N'},
    #     {'AttributeName': 'classroom', 'AttributeType': 'S'},
    #     {'AttributeName': 'days', 'AttributeType': 'S'},
    #     {'AttributeName': 'begin_time', 'AttributeType': 'S'},
    #     {'AttributeName': 'end_time', 'AttributeType': 'S'},
    #     {'AttributeName': 'capacity', 'AttributeType': 'N'},
    #     {'AttributeName': 'waitlist_capacity', 'AttributeType': 'N'},
    #     {'AttributeName': 'freeze', 'AttributeType': 'N'},
    #     {'AttributeName': 'deleted', 'AttributeType': 'N'},
    # ]

def table_create_enrollments(db):
    if table_exists(db, 'Enrollments'): return

    table = db.create_table(
        TableName = 'Enrollments',
        KeySchema=[
            {'AttributeName': 'section_id', 'KeyType': 'HASH'},
            {'AttributeName': 'student_id', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'student_id', 'AttributeType': 'N'},
            {'AttributeName': 'section_id', 'AttributeType': 'N'}
        ],
        ProvisionedThroughput= {
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.wait_until_exists() 

    ## other attributes:
    # AttributeDefinitions=[
    #     {'AttributeName': 'status', 'AttributeType': 'S'},
    #     {'AttributeName': 'date', 'AttributeType': 'S'},
    # ]

if __name__ == "__main__":
    db = get_db()
    table_create_courses(db)
    table_create_sections(db)
    table_create_enrollments(db)

'''
To create a GSI, add the following as an argument to the table_create:

GlobalSecondaryIndexes=[
    {
        'IndexName': '<table>_indexes',
        'KeySchema': [
        {
            'AttributeName': '<attr_name>',
            'KeyType': 'HASH'
        }
        ],
        'Projection': {
            'ProjectionType': 'ALL'
        },
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    }
],
'''