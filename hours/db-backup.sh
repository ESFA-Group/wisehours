#!/bin/bash

set -e
PATH="/usr/local/bin:/usr/bin:/bin"

# Get the date
_d="$(date +'%F')"

# open database, wait up to 1 seconds for any activity to end and create a backup file
sqlite3 /home/mrn/hours/hours/db.sqlite3 ".backup /home/mrn/hours/hours/db_${_d}.sqlite3"

gdrive files upload --parent 1JbFc6ECZQmWuDgzXF3ZQ7VCE7HxJwdDO /home/mrn/hours/hours/db_${_d}.sqlite3

rm /home/mrn/hours/hours/db_${_d}.sqlite3