import datetime
import enum
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict


class Field(enum.Enum):
    Created = 100  # a virtual field, indicating the creation event
    Assignee = 200
    Status = 300
    Resolution = 400


@dataclass
class Event:
    reporter: Optional[str]
    reporter_id: Optional[str]
    assignee: Optional[str]
    assignee_id: Optional[str]
    field: Field
    created: datetime.datetime
    status: Optional[str]
    resolution: Optional[str]


@dataclass
class TimelineItem:
    status: List[str]
    assignee: List[str]


@dataclass
class JiraIssue:
    # facts
    key: str  # issue.key
    project: str  # issue.fields.project.key
    type: str  # issue.fields.issuetype.name
    status: str  # issue.fields.status.name
    created: datetime.datetime  # issue.fields.created
    creator: str  # issue.fields.creator.displayName
    creator_id: str  # issue.fields.creator.key
    reporter: str  # issue.fields.reporter.displayName
    reporter_id: str  # issue.fields.reporter.key
    summary: str  # issue.fields.summary
    assignee: Optional[str]  # issue.fields.assignee.displayName
    assignee_id: Optional[str]  # issue.fields.assignee.key
    updated: Optional[datetime.datetime]  # issue.fields.updated
    resolved: Optional[datetime.datetime]  # issue.fields.resolutiondate
    resolution: Optional[str]  # issue.fields.resolution.name
    due_date: Optional[str]  # issue.fields.duedate
    description: Optional[str]  # issue.fields.description
    labels: List[str]  # issue.fields.labels
    links: List[Tuple[str, str]]  # issue.fields.issuelinks
    components: List[str]  # issue.fields.components
    custom_fields: Dict[str, str]  # json
    # derived dimensions
    event_log: List[Event]  # computed
    time_in_status: Dict[str, float]  # computed
    time_per_assignee: Dict[str, float]  # computed
    timeline: Dict[datetime.date, TimelineItem]  # computed

