from __future__ import annotations

from typing import ForwardRef, TypedDict

import pytest

from mashumaro.core.const import PY_39_MIN
from mashumaro.core.meta.helpers import get_function_arg_annotation
from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.models import (
    JSONObjectSchema,
    JSONSchema,
    JSONSchemaInstanceType,
)


class MyTypedDict(TypedDict):
    x: int


@pytest.mark.skipif(
    not PY_39_MIN,
    reason=(
        "On Python 3.8 ForwardRef doesn't have __forward_module__ "
        "which is needed here"
    ),
)
def test_jsonschema_generation_for_forward_refs():
    def foo(x: int, y: MyTypedDict):
        pass

    x_type = get_function_arg_annotation(foo, "x")
    assert isinstance(x_type, ForwardRef)
    assert build_json_schema(x_type).type is JSONSchemaInstanceType.INTEGER

    y_type = get_function_arg_annotation(foo, "y")
    assert isinstance(y_type, ForwardRef)
    assert build_json_schema(y_type) == JSONObjectSchema(
        type=JSONSchemaInstanceType.OBJECT,
        properties={"x": JSONSchema(type=JSONSchemaInstanceType.INTEGER)},
        additionalProperties=False,
        required=["x"],
    )
