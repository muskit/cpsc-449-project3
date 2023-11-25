from typing import Generator
import boto3
from botocore.exceptions import ClientError

def get_db():
	return boto3.resource('dynamodb', endpoint_url = 'http://localhost:8000')

def table_exists(db, table_name):
	try:
		# Try to describe the table
		db.meta.client.describe_table(TableName=table_name)
		return True
	except ClientError as e:
		if e.response['Error']['Code'] == 'ResourceNotFoundException':
			# Table not found
			return False
		else:
			# Unexpected error
			raise