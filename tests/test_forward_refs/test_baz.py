from __future__ import annotations

from dataclasses import dataclass

from .test_foobar import Bar, Foo


@dataclass
class Baz(Foo[int]):
    pass


def test_class_with_base_in_another_module():
    assert Bar(x=1).to_json() == '{"x": 1}'
    assert Baz(x=1).to_json() == '{"x": 1}'
