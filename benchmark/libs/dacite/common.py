from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Optional, Union

import pyperf
from dacite import Config, from_dict

from benchmark.common import AbstractBenchmark


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


@dataclass
class User:
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
    starred_at: Optional[datetime] = None


@dataclass
class IssueLabel:
    id: int
    node_id: str
    url: str
    name: str
    description: Optional[str]
    color: Optional[str]
    default: bool


@dataclass
class Milestone:
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
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    due_on: Optional[datetime]
    state: MilestoneState = MilestoneState.OPEN


@dataclass
class Reactions:
    url: str
    total_count: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int
    # dacite doesn't have aliases, so we're using default
    plus_one: int = 0
    minus_one: int = 0


@dataclass
class Issue:
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    number: int
    state: IssueState
    state_reason: Optional[IssueStateReason]
    title: str
    body: Optional[str]
    user: Optional[User]
    labels: list[Union[IssueLabel, str]]
    assignee: Optional[User]
    assignees: Optional[list[User]]
    milestone: Optional[Milestone]
    locked: bool
    active_lock_reason: Optional[str]
    comments: int
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    closed_by: Optional[User]
    author_association: AuthorAssociation
    draft: bool = False
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    timeline_url: Optional[str] = None
    reactions: Optional[Reactions] = None


class Benchmark(AbstractBenchmark):
    LIBRARY = "dacite"

    def __init__(self, runner: pyperf.Runner):
        super().__init__(runner)
        self._config = Config(
            type_hooks={datetime: datetime.fromisoformat},
            cast=[Enum],
            check_types=False,
        )

    def warmup(self, data) -> None:
        from_dict(Issue, data, config=self._config)

    def run_loader(self, data) -> pyperf.Benchmark:
        return self._bench_loader_func(
            partial(from_dict, Issue, config=self._config), data
        )
