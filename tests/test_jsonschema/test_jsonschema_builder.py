import json
from dataclasses import dataclass

from typing_extensions import Literal, TypeVarTuple

from mashumaro.config import BaseConfig
from mashumaro.jsonschema import DRAFT_2020_12, OPEN_API_3_1
from mashumaro.jsonschema.builder import JSONSchemaBuilder, build_json_schema
from mashumaro.jsonschema.schema import Instance

Ts = TypeVarTuple("Ts")


@dataclass
class A:
    a: int


@dataclass
class B:
    b: float


def test_instance():
    @dataclass
    class DataClass:
        class Config(BaseConfig):
            pass

    instance = Instance(int)
    assert instance.metadata == {}
    assert instance.owner_class is None
    assert instance.metadata == {}
    assert instance.get_self_config() is BaseConfig

    instance = Instance(DataClass)
    assert instance.owner_class is None
    assert instance.metadata == {}
    assert instance.get_self_config() is DataClass.Config

    derived_instance = instance.derive(type=int)
    assert derived_instance.owner_class is DataClass
    assert derived_instance.metadata == {}
    assert derived_instance.get_self_config() is BaseConfig


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


def test_jsonschema_builder_draft_2020_12():
    builder = JSONSchemaBuilder(dialect=DRAFT_2020_12)
    assert builder.build(A).to_dict() == {
        "type": "object",
        "title": "A",
        "properties": {"a": {"type": "integer"}},
        "additionalProperties": False,
        "required": ["a"],
    }
    assert builder.get_definitions().to_dict() == {}


def test_jsonschema_builder_draft_2020_12_with_refs():
    builder = JSONSchemaBuilder(dialect=DRAFT_2020_12, all_refs=True)
    assert builder.build(A).to_dict() == {"$ref": "#/$defs/A"}
    assert builder.build(B).to_dict() == {"$ref": "#/$defs/B"}
    assert builder.get_definitions().to_dict() == {
        "A": {
            "type": "object",
            "title": "A",
            "properties": {"a": {"type": "integer"}},
            "additionalProperties": False,
            "required": ["a"],
        },
        "B": {
            "type": "object",
            "title": "B",
            "properties": {"b": {"type": "number"}},
            "additionalProperties": False,
            "required": ["b"],
        },
    }


def test_jsonschema_builder_open_api_3_1():
    builder = JSONSchemaBuilder(dialect=OPEN_API_3_1)
    assert builder.build(A).to_dict() == {"$ref": "#/components/schemas/A"}
    assert builder.build(B).to_dict() == {"$ref": "#/components/schemas/B"}
    assert builder.get_definitions().to_dict() == {
        "A": {
            "type": "object",
            "title": "A",
            "properties": {"a": {"type": "integer"}},
            "additionalProperties": False,
            "required": ["a"],
        },
        "B": {
            "type": "object",
            "title": "B",
            "properties": {"b": {"type": "number"}},
            "additionalProperties": False,
            "required": ["b"],
        },
    }


def test_jsonschema_builder_open_api_3_1_without_refs():
    builder = JSONSchemaBuilder(dialect=OPEN_API_3_1, all_refs=False)
    assert builder.build(A).to_dict() == {
        "type": "object",
        "title": "A",
        "properties": {"a": {"type": "integer"}},
        "additionalProperties": False,
        "required": ["a"],
    }
    assert builder.build(B).to_dict() == {
        "type": "object",
        "title": "B",
        "properties": {"b": {"type": "number"}},
        "additionalProperties": False,
        "required": ["b"],
    }
    assert builder.get_definitions().to_dict() == {}
