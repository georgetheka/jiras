#!/usr/bin/env bash

# default connection details for the local postgres db
CONN_STRING=postgres://jiras:jiras@localhost:5432/jiras

# enable python virtual environment
python3 -m venv ./venv
. ./venv/bin/activate

# install dependencies
pip install jira==3.0.1
pip install psycopg2==2.8.4

# initialize and create the database
psql -f ./jiras/sql/create_db.sql
