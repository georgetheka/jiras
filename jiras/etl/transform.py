import collections
import datetime
from typing import List, Optional, Dict, Any, Tuple

from jiras.etl.types import Event, Field, JiraIssue, TimelineItem

_STATUS = 'status'
_ASSIGNEE = 'assignee'
_VAL_RESOLUTION = 'resolution'


def _parse_datetime(value: str) -> datetime.datetime:
    return datetime.datetime.strptime(value[:-9], '%Y-%m-%dT%H:%M:%S')


def _parse_issue_changelog(issue) -> List[Event]:
    assignee = None
    assignee_id = None
    status = None
    resolution = None

    changelog: List[Event] = [
        Event(
            reporter=issue.fields.reporter.displayName if issue.fields.reporter else '',
            reporter_id=issue.fields.reporter.key if issue.fields.reporter else '',
            assignee=None,
            assignee_id=None,
            field=Field.Created,
            created=_parse_datetime(issue.fields.created),
            status=None,
            resolution=None
        )
    ]

    for h in issue.changelog.histories:
        for item in h.items:
            field: Optional[Field] = None

            if item.field == _STATUS:
                status = item.toString
                field = Field.Status
            elif item.field == _ASSIGNEE:
                assignee = item.toString
                assignee_id = item.to
                field = Field.Assignee
            elif item.field == _VAL_RESOLUTION:
                field = Field.Resolution
                resolution = item.toString
            else:
                pass

            if field:
                changelog.append(Event(
                    reporter=None,
                    reporter_id=None,
                    assignee=assignee,
                    assignee_id=assignee_id,
                    field=field,
                    created=_parse_datetime(h.created),
                    status=status,
                    resolution=resolution,
                ))

    return changelog


def _diff_days(d1, d2) -> float:
    diff = d1 - d2
    diff = diff.days + diff.seconds / 3600.0 / 24.0
    # removing the weekend days from the total
    diff = diff - float(_num_weekend_days(d1, d2))
    return diff if diff > 0.01 else 0.0


def _num_weekend_days(d1, d2, excluded=(6, 7)) -> int:
    n = 0
    while d1.date() <= d2.date():
        if d1.isoweekday() in excluded:
            n += 1
        d1 += datetime.timedelta(days=1)
    return n


def _parse_stats(changelog: List[Event]) -> Tuple[Dict, Dict]:
    s = collections.OrderedDict()
    a = collections.OrderedDict()
    if not changelog:
        return s, a

    prev_status_created = None
    prev_status = None

    prev_assignee_created = None
    prev_assignee = None

    for e in changelog:
        if e.field == Field.Status:
            if e.status not in s:
                s[e.status] = 0.0
                if prev_status:
                    s[prev_status] += _diff_days(e.created, prev_status_created)
                prev_status = e.status
                prev_status_created = e.created

        elif e.field == Field.Assignee and e.assignee is not None:
            if e.assignee not in a:
                a[e.assignee] = 0.0
            if prev_assignee:
                a[prev_assignee] += _diff_days(e.created, prev_assignee_created)
            prev_assignee = e.assignee
            prev_assignee_created = e.created

    now = datetime.datetime.now()
    if prev_status_created:
        s[prev_status] += _diff_days(now, prev_status_created)
    if prev_assignee_created:
        a[prev_assignee] += _diff_days(now, prev_assignee_created)
    return s, a


def parse_jira_issue(issue: Any) -> JiraIssue:
    log = _parse_issue_changelog(issue)
    time_in_status, time_per_assignee = _parse_stats(log)

    f = issue.fields

    return JiraIssue(
        labels=f.labels,
        type=f.issuetype.name,
        links=[
            (l.inwardIssue.key if hasattr(l, 'inwardIssue') else l.outwardIssue.key, l.type.name)
            for l in f.issuelinks
        ],
        due_date=f.duedate,
        project=f.project.key,
        reporter=f.reporter.displayName if f.reporter else '',
        reporter_id=f.reporter.key if f.reporter else '',
        summary=f.summary,
        updated=_parse_datetime(f.updated) if f.updated else None,
        resolved=_parse_datetime(f.resolutiondate) if f.resolutiondate else None,
        created=_parse_datetime(f.created),
        description=f.description,
        components=f.components,
        creator=f.creator.displayName,
        creator_id=f.creator.key,
        key=issue.key,
        status=f.status.name,
        assignee=f.assignee.displayName if f.assignee else None,
        assignee_id=f.assignee.key if f.assignee else None,
        resolution=f.resolution.name if f.resolution else None,
        event_log=log,
        time_in_status=time_in_status,
        time_per_assignee=time_per_assignee,
        timeline=_parse_timeline(log),
        custom_fields={
            k: [str(x) for x in v] if isinstance(v, list) else str(v)
            for k, v in issue.fields.__dict__.items()
            if k.startswith('customfield_') and v is not None
        }
    )


def _parse_timeline(log: List) -> Dict[datetime.date, TimelineItem]:
    created_event = log[0]
    last_event = log[-1]
    first_date = created_event.created.date()
    last_date = last_event.created.date()
    num_days = (last_date - first_date).days

    # create a dictionary of dates with range from the first to the last event
    dates = {
        first_date + datetime.timedelta(days=x): TimelineItem(status=[], assignee=[])
        for x in range(num_days + 1)
    }

    # fill out the dates dictionary with the current events
    for e in log:
        if e.field == Field.Created:
            dates[e.created.date()].status.append(f'Created<{created_event.reporter}>')
        elif e.field == Field.Status:
            dates[e.created.date()].status.append(e.status)
        elif e.field == Field.Assignee and e.assignee is not None:
            dates[e.created.date()].assignee.append(e.assignee)
        else:
            resolution = f'<{e.resolution}>' if e.resolution else ''
            dates[e.created.date()].status.append(f'Resolved{resolution}')

    # fill out empty dates with previous values for assignee and status
    status = None
    assignee = None
    for k, v in dates.items():
        if v.status:
            status = v.status[-1]
        elif status:
            v.status.append(status)

        if v.assignee:
            assignee = v.assignee[-1]
        elif assignee:
            v.assignee.append(assignee)

    return dates
