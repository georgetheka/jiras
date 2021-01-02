CONN_STRING=postgres://jiras:jiras@localhost:5432/jiras

.PHONY: all
all: install

.PHONY: install
install:
	pip install jira
	pip install psycopg2
	psql -f ./jiras/sql/create_db.sql
