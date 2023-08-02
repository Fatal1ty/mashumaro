from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

import cattr
import cattrs.gen
import pyperf

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


@dataclass(slots=True)
class User:
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


@dataclass(slots=True)
class IssueLabel:
    id: int
    node_id: str
    url: str
    name: str
    description: Optional[str]
    color: Optional[str]
    default: bool


@dataclass(slots=True)
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


@dataclass(slots=True)
class Reactions:
    url: str
    total_count: int
    plus_one: int
    minus_one: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


@dataclass(slots=True)
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
    LIBRARY = "cattrs"

    def __init__(self, runner: pyperf.Runner):
        super().__init__(runner)
        self._converter = cattr.Converter(detailed_validation=False)
        self._converter.register_structure_hook(
            Reactions,
            cattr.gen.make_dict_structure_fn(
                Reactions,
                self._converter,
                plus_one=cattrs.gen.override(rename="+1"),
                minus_one=cattrs.gen.override(rename="-1"),
            ),
        )
        self._converter.register_unstructure_hook(
            Reactions,
            cattr.gen.make_dict_unstructure_fn(
                Reactions,
                self._converter,
                plus_one=cattrs.gen.override(rename="+1"),
                minus_one=cattrs.gen.override(rename="-1"),
            ),
        )
        self._converter.register_structure_hook(
            datetime, lambda o, _: datetime.fromisoformat(o)
        )
        self._converter.register_unstructure_hook(
            datetime, lambda o: o.isoformat()
        )
        self._converter.register_structure_hook(
            Union[IssueLabel, str],
            lambda o, _: self._converter.structure(
                o, IssueLabel if isinstance(o, dict) else str
            ),
        )

    def warmup(self, data: Dict[str, Any]):
        self._converter.unstructure(self._converter.structure(data, Issue))

    def run_loader(self, data: Dict[str, Any]) -> pyperf.Benchmark:
        return self._bench_loader_func(self._converter.structure, data, Issue)

    def run_dumper(self, data: Dict[str, Any]) -> pyperf.Benchmark:
        obj = self._converter.structure(data, Issue)
        return self._bench_dumper_func(self._converter.unstructure, obj)
