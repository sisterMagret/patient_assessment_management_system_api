#!/bin/bash

sudo su postgres << EOF

psql -c "CREATE DATABASE pms;"
# psql -c "CREATE USER admin WITH ENCRYPTED PASSWORD 'adminpassword';"
# psql -c "ALTER ROLE admin SET client_encoding TO 'utf8';"
# psql -c "ALTER ROLE admin SET default_transaction_isolation TO 'read committed';"
# psql -c "ALTER ROLE admin SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO admin;"

echo "Postgres User admin and database pms created."

EOF
