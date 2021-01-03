#!/bin/bash

set -euo pipefail

# Wait for mysql to start
echo Waiting $MYSQL_STARTUP_DELAY_SECONDS seconds before webserver startup
sleep $MYSQL_STARTUP_DELAY_SECONDS

# construct empty database
python3 bmf_web/manage.py makemigrations
python3 bmf_web/manage.py migrate

#run example BMF job
python3 bmf_web/manage.py run_example

# start webserver
python3 bmf_web/manage.py runserver 0.0.0.0:10080

