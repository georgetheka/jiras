# JIRAS

This is an ETL that extracts JIRA data based on a specific query. It then transforms the data into a simpler model, it computes several useful analytics that are typically
non-trivial analytics such as time in status and timeline. Finally it loads the data into a postgres instance as a mini data-warehouse that
can enable key metrics analysis.

#### Requirements

* bash
* python3
* postgres
* jira access

NOTE: The JIRA data set mapped through this process is typically small regardless of organization size and this solution
could have been implemented with just sqlite. However, Postgres brings in a few features to easily deal with non-tabular data
such as array and json fields.

#### Installation

Run

```
make
```

to install dependencies and create the postgres database

Setup the jira credentials as environment variables

```
JIRA_USER=<username>
JIRA_PASS=<password>
```

#### Usage

To use run

```
jiras.sh -j https://myjirainstance.example.com -q "project in (Personal, Finance, Marketing)"
```

For more info run

```
jiras.sh -h
```
 
The output of the help option is also included here for convenience:

```$bash
Usage: jiras -- runs the jira etl process

SYNOPSIS
    jiras [-h | -j <jira-server-url> -q <jira-query> [-l <jira-query-limit>]]

OPTIONS
    -h      : displays usage information
    -j      : specify the jira server url (e.g. https://myjirainstance.example.com)
    -q      : specify the jira query statement (e.g. "project in (X, Y, Z)")
    -l      : specify the jira query limit (e.g. 150), defaults to "1000"
```

### Data

The following tables are created:

`issue` - this is the fact table at the center of this schema

|Field|Type|
|---|---|
| id            | integer                     |
| ingested_at   | timestamp without time zone |
| key           | character varying(16)       |
| project       | character varying(64)       |
| type          | character varying(64)       |
| status        | character varying(64)       |
| created       | timestamp without time zone |
| creator       | character varying(64)       |
| creator_id    | character varying(16)       |
| reporter      | character varying(64)       |
| reporter_id   | character varying(16)       |
| summary       | character varying(512)      |
| assignee      | character varying(64)       |
| assignee_id   | character varying(16)       |
| updated       | timestamp without time zone |
| resolved      | timestamp without time zone |
| resolution    | character varying(64)       |
| due_date      | timestamp without time zone |
| description   | character varying           |
| labels        | character varying(64)[]     |
| components    | character varying(64)[]     |
| links         | jsonb                       |
| custom_fields | jsonb                       |
 
 `event_log` - contains a log trail for the most critical events that include:
 
 * creation 
 * assignee change
 * status change
 * resolution
 
 It is important to note a few important fields:
 
 * `custom_fields` is a json document that contains all JIRA's custom configurations that vary per 
 organization and deploy. Important facts, such as story points, sprint data, are typically present as a custom field.
 
 In that case, it is recommended to create a view that maps critical custom fields. For example, `customfield_12345` can be mapped as:
 
 ```
 create view myview as (
    select
        ...
        custom_fields ->> 'customfield_12345' as myfield,
        ....
    from issue)
 ```
 
 
|Field|Type|
|---|---|
|  id          | bigint                      |
|  ingested_at | timestamp without time zone |
|  issue_key   | character varying(16)       |
|  field       | character varying(32)       |
|  reporter    | character varying(64)       |
|  reporter_id | character varying(16)       |
|  assignee    | character varying(64)       |
|  assignee_id | character varying(16)       |
|  created     | timestamp without time zone |
|  status      | character varying(64)       |
|  resolution  | character varying(64)       |
 
 
`time_in_status` - (dimension) days spent in each status for any given issue.

|Field|Type|
|---|---|
| id          | bigint                      |
| ingested_at | timestamp without time zone |
| issue_key   | character varying(16)       |
| status      | character varying(64)       |
| days        | numeric                     |



`timeline` - (dimension) a time-series version of the event-log which simplifies inspecting process bottlenecks. 
an event activity on that day.  

|Field|Type|
|---|---|
 id          | bigint                      |
 ingested_at | timestamp without time zone |
 issue_key   | character varying(16)       |
 d           | date                        |
 status      | character varying(64)[]     |
 assignee    | character varying(64)[]     |
 

`time_per_assignee` - (dimension) days spent per assignee.
I need to emphasize that this data should never be used for
performance evaluation purposes because in an agile team the assignee field
does not capture team effort and collaboration well. But it can be helpful
in understanding work distribution in a cross-functional team when assignees
are grouped by function.

|Field|Type|
|---|---|
| id          | bigint                      |
| ingested_at | timestamp without time zone |
| issue_key   | character varying(16)       |
| assignee    | character varying(64)       |
| days        | numeric                     |


### Next Steps

This ETL provides the foundational schema for analysis. However, in most cases, this is not enough.
That's because each organization has its own unique JIRA configuration of workflows and custom fields. A derived layer of views
can help provide the specific organizational context and only then the data the data is ready for exploration with your
favorite data science stack, like spinning up a jupiter-lab notebook with pandas and sql support. 
