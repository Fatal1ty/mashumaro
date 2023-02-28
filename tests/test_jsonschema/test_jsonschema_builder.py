import json
from dataclasses import dataclass

from typing_extensions import Literal, TypeVarTuple

from mashumaro.jsonschema.builder import build_json_schema
from mashumaro.jsonschema.schema import Instance

Ts = TypeVarTuple("Ts")


def test_instance():
    @dataclass
    class DataClass:
        pass

    instance = Instance(int)
    assert instance.metadata == {}
    assert instance.holder_class is None

    instance = Instance(DataClass)
    assert instance.holder_class is DataClass
    assert instance.metadata == {}


def test_jsonschema_json_simple():
    assert json.loads(build_json_schema(int).to_json()) == {"type": "integer"}


def test_jsonschema_json_literal_none():
    @dataclass
    class DataClass:
        x: Literal[None] = None

    assert json.loads(build_json_schema(DataClass).to_json()) == {
        "type": "object",
        "title": "DataClass",
        "properties": {"x": {"const": None, "default": None}},
        "additionalProperties": False,
    }
