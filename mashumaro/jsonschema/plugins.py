from dataclasses import is_dataclass
from typing import Optional

from mashumaro.jsonschema.models import Context, JSONSchema
from mashumaro.jsonschema.schema import Instance


class BasePlugin:
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: Optional[JSONSchema] = None,
    ):
        pass


class DocstringDescriptionPlugin(BasePlugin):
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: Optional[JSONSchema] = None,
    ):
        if schema and is_dataclass(instance.type) and instance.type.__doc__:
            schema.description = instance.type.__doc__
