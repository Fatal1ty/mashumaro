from dataclasses import dataclass
from typing_extensions import Annotated

from mashumaro.jsonschema.builder import build_json_schema
from mashumaro.jsonschema.schema import (
    JSONSchemaInstanceFormatExtension,
    JSONSchemaStringFormat,
)


@dataclass
class User:
    email: Annotated[str, JSONSchemaStringFormat.EMAIL]
    small_image: Annotated[str, JSONSchemaInstanceFormatExtension.BASE64]


def test_jsonschema_string_format():
    schema = build_json_schema(User)
    assert schema.properties["email"].format == JSONSchemaStringFormat.EMAIL
    assert (
        schema.properties["small_image"].format
        == JSONSchemaInstanceFormatExtension.BASE64
    )
