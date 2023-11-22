#!/bin/sh
set -e

if ! PATH="$PATH":run/bin command -v litefs >/dev/null 2>&1; then
	echo "litefs isn't even installed, did you run ./install_deps.sh?" >&2
	exit 1
fi

echo "MAKE SURE YOU'VE STARTED THE Procfile BEFORE RUNNING THIS!"
echo "IF YOU HAVEN'T, [CTRL+C] NOW AND START IT."
read  -n 1 -p "Otherwise, press any key to continue with DB initialization." mainmenuinput

echo "Initializing enrollment database..."
python3 -m services.enrollment.schema_init
echo

echo "Initializing authentication database..."
python3 -m services.authentication.schema_init
echo

