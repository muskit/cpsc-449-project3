import boto3
from internal.database_dynamo import get_db, table_exists

if __name__ == '__main__':
	# Create the DynamoDB client
	db = get_db()

	if table_exists(db, 'Enrollments'):
		db.Table('Enrollments').delete()

	if table_exists(db, 'Sections'):
		db.Table('Sections').delete()

	if table_exists(db, 'Courses'):
		db.Table('Courses').delete()
