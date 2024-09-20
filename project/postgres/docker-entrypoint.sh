#!/bin/bash
set -e

# Ensure init.sql exists before trying to process it
if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
    # Directly overwrite the init.sql file using envsubst
    envsubst < /docker-entrypoint-initdb.d/init.sql > /docker-entrypoint-initdb.d/init.sql.tmp
    cat /docker-entrypoint-initdb.d/init.sql.tmp > /docker-entrypoint-initdb.d/init.sql
    echo "Environment variables substituted in init.sql"
    rm /docker-entrypoint-initdb.d/init.sql.tmp
else
    echo "init.sql not found, skipping envsubst step"
fi

# Run the official postgres entrypoint
exec docker-entrypoint.sh "$@"