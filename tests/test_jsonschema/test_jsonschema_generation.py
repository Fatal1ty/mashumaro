from typing import Any, List, Tuple

from mashumaro.jsonschema.builder import build_json_schema
from mashumaro.jsonschema.models import (
    JSONArraySchema,
    JSONSchema,
    JSONSchemaInstanceType,
)


def test_jsonschema_for_list():
    assert build_json_schema(List[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(List) == JSONArraySchema()


def test_jsonschema_for_tuple():
    assert build_json_schema(Tuple[int]) == JSONArraySchema(
        prefixItems=[JSONSchema(type=JSONSchemaInstanceType.INTEGER)],
        maxItems=1,
        minItems=1,
    )
    assert build_json_schema(Tuple) == JSONArraySchema()
    assert build_json_schema(Tuple[()]) == JSONArraySchema(maxItems=0)
    assert build_json_schema(Tuple[Any]) == JSONArraySchema(
        prefixItems=[JSONSchema()], maxItems=1, minItems=1
    )
    assert build_json_schema(Tuple[Any, ...]) == JSONArraySchema()
    assert build_json_schema(Tuple[int, ...]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
