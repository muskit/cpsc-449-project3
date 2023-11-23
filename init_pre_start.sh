#!/bin/sh
echo "Initializing new JWT keys..."
python3 -m internal.jwt_init
echo

echo "Creating directories..."
mkdir -p ./run/enrollment_db