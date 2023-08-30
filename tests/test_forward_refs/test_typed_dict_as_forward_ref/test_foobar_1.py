from __future__ import annotations

from dataclasses import dataclass

from mashumaro import DataClassDictMixin

from .foo import Foo


@dataclass
class FooBar(DataClassDictMixin):
    foo: Foo


def test_foobar():
    obj = FooBar.from_dict({"foo": {"bar": {"baz": "baz"}}})
    assert obj.foo["bar"]["baz"] == "baz"
    assert obj.to_dict() == {"foo": {"bar": {"baz": "baz"}}}
