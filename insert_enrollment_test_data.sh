#!/usr/bin/env bash

echo "Make sure you're running this while the relevant server"
echo "databases (DynamoDB and Redis) are running!"

echo "Press any key to continue or CTRL+C to not create test data."
read -s -n 1
echo

python3 -m services.enrollment.dynamodb_test_data
python3 -m services.enrollment.redis_insert_sample
