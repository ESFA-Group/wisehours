#!/bin/bash

# Get the day of week
_dow="$(date +'%A')"

# open database, wait up to 1 seconds for any activity to end and create a backup file
sqlite3 db.sqlite3 << EOF
.timeout 1000
.backup /backups/db_${_dow}.sqlite3
EOF