from mashumaro.core.meta.types.common import clean_id
from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.models import Context
from mashumaro.jsonschema.schema import _type_alias_definition_name

type JSON = int | str | float | bool | None | list[JSON] | dict[str, JSON]
type X = int | str
type A = int | list[B]
type B = str | list[A]


def test_type_alias_type_with_jsonschema():
    schema = build_json_schema(X)
    assert schema.to_dict() == {
        "anyOf": [{"type": "integer"}, {"type": "string"}]
    }


def test_jsonschema_for_recursive_union() -> None:
    schema = build_json_schema(JSON)
    assert schema.to_dict() == {
        "$ref": "#/$defs/JSON",
        "$defs": {
            "JSON": {
                "anyOf": [
                    {"type": "integer"},
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                    {"type": "null"},
                    {"type": "array", "items": {"$ref": "#/$defs/JSON"}},
                    {
                        "type": "object",
                        "additionalProperties": {"$ref": "#/$defs/JSON"},
                        "propertyNames": {"type": "string"},
                    },
                ]
            }
        },
    }


def test_jsonschema_for_mutual_recursive_type_aliases_without_refs() -> None:
    schema = build_json_schema(A)
    assert schema.to_dict() == {
        "$ref": "#/$defs/A",
        "$defs": {
            "A": {
                "anyOf": [
                    {"type": "integer"},
                    {
                        "type": "array",
                        "items": {
                            "anyOf": [
                                {"type": "string"},
                                {
                                    "type": "array",
                                    "items": {"$ref": "#/$defs/A"},
                                },
                            ]
                        },
                    },
                ]
            }
        },
    }


def test_jsonschema_for_mutual_recursive_type_aliases_with_refs() -> None:
    schema = build_json_schema(A, all_refs=True)
    assert schema.to_dict() == {
        "$ref": "#/$defs/A",
        "$defs": {
            "A": {
                "anyOf": [
                    {"type": "integer"},
                    {"type": "array", "items": {"$ref": "#/$defs/B"}},
                ]
            },
            "B": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"$ref": "#/$defs/A"}},
                ]
            },
        },
    }


def test_type_alias_non_recursive_inlines_when_all_refs_false() -> None:
    schema = build_json_schema(X, all_refs=False)
    assert schema.to_dict() == {
        "anyOf": [
            {"type": "integer"},
            {"type": "string"},
        ]
    }


def test_type_alias_non_recursive_uses_defs_when_all_refs_true() -> None:
    schema = build_json_schema(X, all_refs=True)
    assert schema.to_dict() == {
        "$ref": "#/$defs/X",
        "$defs": {
            "X": {
                "anyOf": [
                    {"type": "integer"},
                    {"type": "string"},
                ]
            }
        },
    }


def test_type_alias_placeholder_not_leaking_into_context_defs() -> None:
    # Ensure that for non-recursive aliases with all_refs=False we don't leave
    # unused entries in Context.definitions.
    ctx = Context()
    schema = build_json_schema(X, context=ctx, all_refs=False)
    assert schema.to_dict() == {
        "anyOf": [
            {"type": "integer"},
            {"type": "string"},
        ]
    }
    assert ctx.definitions == {}


def test_type_alias_definition_name_falls_back_to_clean_id_when_name_empty() -> (
    None
):
    class NamelessAlias:
        __name__ = ""

    alias = NamelessAlias()

    assert _type_alias_definition_name(alias) == clean_id(str(id(alias)))
