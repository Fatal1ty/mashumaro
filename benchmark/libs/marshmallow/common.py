from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import pyperf
from marshmallow import Schema, fields, post_load

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
    plus_one: int
    minus_one: int
    laugh: int
    confused: int
    heart: int
    hooray: int
    eyes: int
    rocket: int


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


class UserSchema(Schema):
    login = fields.Str()
    id = fields.Int()
    node_id = fields.Str()
    avatar_url = fields.Str()
    gravatar_id = fields.Str(allow_none=True)
    url = fields.Str()
    html_url = fields.Str()
    followers_url = fields.Str()
    following_url = fields.Str()
    gists_url = fields.Str()
    starred_url = fields.Str()
    subscriptions_url = fields.Str()
    organizations_url = fields.Str()
    repos_url = fields.Str()
    events_url = fields.Str()
    received_events_url = fields.Str()
    type = fields.Str()
    site_admin = fields.Bool()
    name = fields.Str(allow_none=True, load_default=True)
    email = fields.Str(allow_none=True, load_default=True)
    starred_at = fields.DateTime(allow_none=True, load_default=None)

    @post_load
    def _make_model(self, data, **kwargs):
        return User(**data)


class IssueLabelSchema(Schema):
    id = fields.Int()
    node_id = fields.Str()
    url = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    color = fields.Str(allow_none=True)
    default = fields.Bool()

    @post_load
    def _make_model(self, data, **kwargs):
        return IssueLabel(**data)


class MilestoneSchema(Schema):
    url = fields.Str()
    html_url = fields.Str()
    labels_url = fields.Str()
    id = fields.Int()
    node_id = fields.Str()
    number = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    creator = fields.Nested(UserSchema(), allow_none=True)
    open_issues = fields.Int()
    closed_issues = fields.Int()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    closed_at = fields.DateTime(allow_none=True)
    due_on = fields.DateTime(allow_none=True)
    state = fields.Enum(
        MilestoneState, load_default=MilestoneState.OPEN, by_value=True
    )

    @post_load
    def _make_model(self, data, **kwargs):
        return Milestone(**data)


class ReactionsSchema(Schema):
    url = fields.Str()
    total_count = fields.Int()
    plus_one = fields.Int(data_key="+1")
    minus_one = fields.Int(data_key="-1")
    laugh = fields.Int()
    confused = fields.Int()
    heart = fields.Int()
    hooray = fields.Int()
    eyes = fields.Int()
    rocket = fields.Int()

    @post_load
    def _make_model(self, data, **kwargs):
        return Reactions(**data)


class IssueLabelSchemaOrStr(fields.Method):
    def __init__(self):
        self._issue_label_schema = IssueLabelSchema()
        super().__init__()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return self._issue_label_schema.load(value)
        except ValueError:
            return str(value)

    def _serialize(self, value, attr, obj, **kwargs):
        return (
            self._issue_label_schema.dump(value)
            if isinstance(value, IssueLabel)
            else value
        )


class IssueSchema(Schema):
    id = fields.Int()
    node_id = fields.Str()
    url = fields.Str()
    repository_url = fields.Str()
    labels_url = fields.Str()
    comments_url = fields.Str()
    events_url = fields.Str()
    html_url = fields.Str()
    number = fields.Int()
    state = fields.Enum(IssueState, by_value=True)
    state_reason = fields.Enum(
        IssueStateReason, allow_none=True, by_value=True
    )
    title = fields.Str()
    body = fields.Str(allow_none=True)
    user = fields.Nested(UserSchema(), allow_none=True)
    labels = fields.List(IssueLabelSchemaOrStr())
    assignee = fields.Nested(UserSchema(), allow_none=True)
    assignees = fields.List(fields.Nested(UserSchema()))
    milestone = fields.Nested(MilestoneSchema(), allow_none=True)
    locked = fields.Bool()
    active_lock_reason = fields.Str(allow_none=True)
    comments = fields.Int()
    closed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    closed_by = fields.Nested(UserSchema(), allow_none=True)
    author_association = fields.Enum(AuthorAssociation, by_value=True)
    draft = fields.Bool(load_default=False)
    body_html = fields.Str(allow_none=True, load_default=None)
    body_text = fields.Str(allow_none=True, load_default=None)
    timeline_url = fields.Str(allow_none=True, load_default=None)
    reactions = fields.Nested(
        ReactionsSchema(), allow_none=True, load_default=None
    )

    @post_load
    def _make_model(self, data, **kwargs):
        return Issue(**data)


class Benchmark(AbstractBenchmark):
    LIBRARY = "marshmallow"

    def __init__(self, runner: pyperf.Runner):
        super().__init__(runner)
        self._issue_schema = IssueSchema()

    def warmup(self, data) -> None:
        self._issue_schema.dump(self._issue_schema.load(data))

    def run_loader(self, data) -> pyperf.Benchmark:
        return self._bench_loader_func(self._issue_schema.load, data)

    def run_dumper(self, data) -> pyperf.Benchmark:
        obj = self._issue_schema.load(data)
        return self._bench_dumper_func(self._issue_schema.dump, obj)
