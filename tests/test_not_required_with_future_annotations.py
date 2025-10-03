from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from typing_extensions import NotRequired

from mashumaro import DataClassDictMixin
from mashumaro.codecs.basic import decode, encode
from mashumaro.jsonschema import build_json_schema


class MyDict(TypedDict):
    a: str
    b: NotRequired[int]


@dataclass
class MyDataClass(DataClassDictMixin):
    data: MyDict


def test_typeddict_with_not_required_and_future_annotations():
    # test workaround for https://github.com/Fatal1ty/mashumaro/issues/292
    assert decode({"a": "test", "b": 42}, MyDict) == {"a": "test", "b": 42}
    assert decode({"a": "test", "b": "42"}, MyDict) == {"a": "test", "b": 42}
    assert decode({"a": "test"}, MyDict) == {"a": "test"}

    assert encode(MyDict(a="test"), MyDict) == {"a": "test"}
    assert encode({"a": "test"}, MyDict) == {"a": "test"}
    assert encode(MyDict(a="test", b=42), MyDict) == {"a": "test", "b": 42}

    assert MyDataClass(MyDict(a="test", b=42)).to_dict() == {
        "data": {"a": "test", "b": 42}
    }
    assert MyDataClass(MyDict(a="test")).to_dict() == {"data": {"a": "test"}}

    assert MyDataClass.from_dict(
        {"data": {"a": "test", "b": 42}}
    ) == MyDataClass(MyDict(a="test", b=42))
    assert MyDataClass.from_dict({"data": {"a": "test"}}) == MyDataClass(
        MyDict(a="test")
    )


def test_jsonschema_for_not_required_and_future_annotations():
    schema = build_json_schema(MyDict).to_dict()
    assert schema == {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "integer"},
        },
        "required": ["a"],
        "additionalProperties": False,
    }
