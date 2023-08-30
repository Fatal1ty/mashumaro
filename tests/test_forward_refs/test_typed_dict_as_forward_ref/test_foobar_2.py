from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import TypedDict

from mashumaro import DataClassDictMixin


class Bar(TypedDict):
    baz: str


class Foo(TypedDict):
    bar: Bar


@dataclass
class FooBar(DataClassDictMixin):
    foo: Foo


def test_foobar():
    obj = FooBar.from_dict({"foo": {"bar": {"baz": "baz"}}})
    assert obj.foo["bar"]["baz"] == "baz"
    assert obj.to_dict() == {"foo": {"bar": {"baz": "baz"}}}
