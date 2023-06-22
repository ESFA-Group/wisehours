#!/bin/bash

# Get the day of week
_dow="$(date +'%A')"

# open database, wait up to 1 seconds for any activity to end and create a backup file
sqlite3 db.sqlite3 << EOF
.timeout 1000
.backup db_${_dow}.sqlite3
EOF

gdrive files upload --parent 1JbFc6ECZQmWuDgzXF3ZQ7VCE7HxJwdDO db_${_dow}.sqlite3

rm db_${_dow}.sqlite3