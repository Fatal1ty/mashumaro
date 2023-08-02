from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import pyperf
from dataclasses_json import DataClassJsonMixin, config

from benchmark.common import AbstractBenchmark

datetime_config = config(
    decoder=datetime.fromisoformat, encoder=datetime.isoformat
)
optional_datetime_config = config(
    decoder=lambda o: datetime.fromisoformat(o) if o is not None else None,
    encoder=lambda o: o.isoformat() if isinstance(o, datetime) else None,
)
enum_config = config(encoder=lambda o: o.value)
optional_enum_config = config(
    encoder=lambda o: o.value if isinstance(o, Enum) else None
)


class IssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class MilestoneState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class IssueStateReason(Enum):
    COMPLETED = "completed"
    REOPENED = "reopened"
    NOT_PLANNED = "not_planned"


class AuthorAssociation(Enum):
    COLLABORATOR = "COLLABORATOR"
    CONTRIBUTOR = "CONTRIBUTOR"
    FIRST_TIMER = "FIRST_TIMER"
    FIRST_TIME_CONTRIBUTOR = "FIRST_TIME_CONTRIBUTOR"
    MANNEQUIN = "MANNEQUIN"
    MEMBER = "MEMBER"
    NONE = "NONE"
    OWNER = "OWNER"


@dataclass(slots=True)
class User(DataClassJsonMixin):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: Optional[str]
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: Optional[str] = None
    email: Optional[str] = None
    starred_at: Optional[datetime] = field(
        default=None, metadata=optional_datetime_config
    )


@dataclass(slots=True)
class IssueLabel(DataClassJsonMixin):
    id: int
    node_id: str
    url: str
    name: str
    description: Optional[str]
    color: Optional[str]
    default: bool


@dataclass(slots=True)
class Milestone(DataClassJsonMixin):
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    title: str
    description: Optional[str]
    creator: Optional[User]
    open_issues: int
    closed_issues: int
    created_at: datetime = field(metadata=datetime_config)
    updated_at: datetime = field(metadata=datetime_config)
    closed_at: Optional[datetime] = field(metadata=optional_datetime_config)
    due_on: Optional[datetime] = field(metadata=optional_datetime_config)
    state: MilestoneState = MilestoneState.OPEN


@dataclass(slots=True)
class Reactions(DataClassJsonMixin):
    url: str
    total_count: int
    plus_one: int = field(metadata=config(field_name="+1"))
    minus_one: int = field(metadata=config(field_name="-1"))
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


@dataclass(slots=True)
class Issue(DataClassJsonMixin):
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    number: int
    state: IssueState = field(metadata=enum_config)
    state_reason: Optional[IssueStateReason] = field(
        metadata=optional_enum_config
    )
    title: str
    body: Optional[str]
    user: Optional[User]
    labels: list[IssueLabel]
    assignee: Optional[User]
    assignees: Optional[list[User]]
    milestone: Optional[Milestone]
    locked: bool
    active_lock_reason: Optional[str]
    comments: int
    closed_at: Optional[datetime] = field(metadata=optional_datetime_config)
    created_at: datetime = field(metadata=datetime_config)
    updated_at: datetime = field(metadata=datetime_config)
    closed_by: Optional[User]
    author_association: AuthorAssociation = field(metadata=enum_config)
    draft: bool = False
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    timeline_url: Optional[str] = None
    reactions: Optional[Reactions] = None


class Benchmark(AbstractBenchmark):
    LIBRARY = "dataclasses-json"

    def warmup(self, data) -> None:
        Issue.from_dict(data).to_dict()

    def run_loader(self, data) -> pyperf.Benchmark:
        return self._bench_loader_func(Issue.from_dict, data)

    def run_dumper(self, data) -> pyperf.Benchmark:
        obj = Issue.from_dict(data)
        return self._bench_dumper_func(obj.to_dict)
