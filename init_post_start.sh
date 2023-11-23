#!/bin/sh
set -e

if ! PATH="$PATH":run/bin command -v litefs >/dev/null 2>&1; then
	echo "litefs isn't even installed, did you run ./install_deps.sh?" >&2
	exit 1
fi

echo "Initializing authentication database..."
python3 -m services.authentication.schema_init
echo

echo "Initializing enrollment database..."
python3 -m services.enrollment.create_dynamodb
echo
