from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import pyperf

from benchmark.common import AbstractBenchmark
from mashumaro import DataClassDictMixin, field_options, pass_through
from mashumaro.config import BaseConfig


class BaseModel(DataClassDictMixin):
    class Config(BaseConfig):
        lazy_compilation = True
        serialize_by_alias = True
        serialization_strategy = {
            str: {"deserialize": str, "serialize": pass_through},
            int: {"serialize": pass_through},
        }


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
class User(BaseModel):
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


@dataclass(slots=True)
class IssueLabel(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    description: Optional[str]
    color: Optional[str]
    default: bool


@dataclass(slots=True)
class Milestone(BaseModel):
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
class Reactions(BaseModel):
    url: str
    total_count: int
    plus_one: int = field(metadata=field_options(alias="+1"))
    minus_one: int = field(metadata=field_options(alias="-1"))
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


@dataclass(slots=True)
class Issue(BaseModel):
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
    LIBRARY = "mashumaro"

    def warmup(self, data) -> None:
        Issue.from_dict(data).to_dict()

    def run_loader(self, data) -> pyperf.Benchmark:
        return self._bench_loader_func(Issue.from_dict, data)

    def run_dumper(self, data) -> pyperf.Benchmark:
        obj = Issue.from_dict(data)
        return self._bench_dumper_func(obj.to_dict)
