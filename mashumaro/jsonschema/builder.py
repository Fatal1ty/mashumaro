from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from mashumaro.jsonschema.dialects import DRAFT_2020_12, JSONSchemaDialect
from mashumaro.jsonschema.models import Context, JSONSchema
from mashumaro.jsonschema.schema import Instance, get_schema

try:
    from mashumaro.mixins.orjson import (
        DataClassORJSONMixin as DataClassJSONMixin,
    )
except ImportError:
    from mashumaro.mixins.json import DataClassJSONMixin  # type: ignore


def build_json_schema(
    instance_type: Type,
    context: Optional[Context] = None,
    with_definitions: bool = True,
) -> JSONSchema:
    if context is None:
        context = Context()
    instance = Instance(instance_type)
    schema = get_schema(instance, context)
    if with_definitions and context.definitions:
        schema.definitions = context.definitions
    return schema


@dataclass
class JSONSchemaDefinitions(DataClassJSONMixin):
    definitions: Dict[str, JSONSchema]

    def __post_serialize__(  # type: ignore
        self, d: Dict[Any, Any]
    ) -> List[Dict[str, Any]]:
        return d["definitions"]


class JSONSchemaBuilder:
    def __init__(
        self,
        dialect: JSONSchemaDialect = DRAFT_2020_12,
    ):
        self.context = Context(dialect=dialect)

    def build(self, instance_type: Type) -> JSONSchema:
        return build_json_schema(
            instance_type=instance_type,
            context=self.context,
            with_definitions=False,
        )

    def get_definitions(self) -> JSONSchemaDefinitions:
        return JSONSchemaDefinitions(self.context.definitions)


__all__ = ["JSONSchemaBuilder"]
