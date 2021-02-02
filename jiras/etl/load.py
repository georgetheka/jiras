import pathlib
import json
from typing import List

from jiras.common.postgres import Postgres
from jiras.etl.types import JiraIssue

_SQL_INSERT_ISSUE = '''
insert into issue (
    key,
    project,
    "type",
    status,
    created,
    creator,
    creator_id, 
    reporter,
    reporter_id,
    summary,
    assignee,
    assignee_id,
    updated,
    resolved,
    resolution,
    due_date,
    description,
    labels,
    links,
    components,
    custom_fields
) values (
    %(key)s,
    %(project)s,
    %(type)s,
    %(status)s,
    %(created)s,
    %(creator)s,
    %(creator_id)s, 
    %(reporter)s,
    %(reporter_id)s,
    %(summary)s,
    %(assignee)s,
    %(assignee_id)s,
    %(updated)s,
    %(resolved)s,
    %(resolution)s,
    %(due_date)s,
    %(description)s,
    %(labels)s,
    %(links)s,
    %(components)s,
    %(custom_fields)s
)
'''

_SQL_INSERT_EVENT_LOG = '''
insert into event_log (
    issue_key,
    field,
    reporter,
    reporter_id,
    assignee,
    assignee_id,
    created,
    status,
    resolution
) values (
    %(issue_key)s,
    %(field)s,
    %(reporter)s,
    %(reporter_id)s,
    %(assignee)s,
    %(assignee_id)s,
    %(created)s,
    %(status)s,
    %(resolution)s
)
'''

_SQL_INSERT_TIME_IN_STATUS = '''
insert into time_in_status (
    issue_key,
    status,
    days
) values (
    %(issue_key)s,
    %(status)s,
    %(days)s
)
'''

_SQL_INSERT_TIME_PER_ASSIGNEE = '''
insert into time_per_assignee (
    issue_key,
    assignee,
    days
) values (
    %(issue_key)s,
    %(assignee)s,
    %(days)s
)
'''

_SQL_INSERT_TIMELINE = '''
insert into timeline (
    issue_key,
    d,
    status,
    assignee
) values (
    %(issue_key)s,
    %(d)s,
    %(status)s,
    %(assignee)s
)
'''


class DataDestination:
    def __init__(self, postgres: Postgres):
        self.postgres = postgres

    def reset_database(self):
        create_schema_filepath = f'{pathlib.Path().absolute()}/jiras/sql/create_schema.sql'
        with open(create_schema_filepath, 'rt', encoding='utf-8') as f:
            statements = ''.join(f.readlines()).split(';')
            statements = [s.strip() for s in statements]
            for stmt in [s for s in statements if s]:
                self.postgres.exec(query=stmt, write_params=[{}])

    def load(self, issues: List[JiraIssue]):
        issue_write_params = []
        event_log_write_params = []
        time_in_status_write_params = []
        time_per_assignee_write_params = []
        timeline_write_params = []

        for i in issues:
            issue_write_params.append({
                'key': i.key,
                'project': i.project,
                'type': i.type,
                'status': i.status,
                'created': i.created,
                'creator': i.creator,
                'creator_id': i.creator_id,
                'reporter': i.reporter,
                'reporter_id': i.reporter_id,
                'summary': i.summary,
                'assignee': i.assignee,
                'assignee_id': i.assignee_id,
                'updated': i.updated,
                'resolved': i.resolved,
                'resolution': i.resolution,
                'due_date': i.due_date,
                'description': i.description,
                'labels': i.labels,
                'links': json.dumps(i.links),
                'components': [c.name for c in i.components],
                'custom_fields': json.dumps(i.custom_fields),
            })

            event_log_write_params.extend([{
                'issue_key': i.key,
                'field': e.field.name,
                'reporter': e.reporter,
                'reporter_id': e.reporter_id,
                'assignee': e.assignee,
                'assignee_id': e.assignee_id,
                'created': e.created,
                'status': e.status,
                'resolution': e.resolution
            } for e in i.event_log])

            time_in_status_write_params.extend([{
                'issue_key': i.key,
                'status': k,
                'days': v,
            } for k, v in i.time_in_status.items()])

            time_per_assignee_write_params.extend([{
                'issue_key': i.key,
                'assignee': k,
                'days': v,
            } for k, v in i.time_per_assignee.items()])

            timeline_write_params.extend([{
                'issue_key': i.key,
                'd': k,
                'status': v.status,
                'assignee': v.assignee,
            } for k, v in i.timeline.items()])

        self.postgres.exec(_SQL_INSERT_ISSUE, write_params=issue_write_params)
        self.postgres.exec(_SQL_INSERT_EVENT_LOG, write_params=event_log_write_params)
        self.postgres.exec(_SQL_INSERT_TIME_IN_STATUS, write_params=time_in_status_write_params)
        self.postgres.exec(_SQL_INSERT_TIME_PER_ASSIGNEE, write_params=time_per_assignee_write_params)
        self.postgres.exec(_SQL_INSERT_TIMELINE, write_params=timeline_write_params)
