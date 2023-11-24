import boto3

# Create the DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

table = dynamodb.Table('EnrollmentService')
table.delete()
