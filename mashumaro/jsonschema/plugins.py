from dataclasses import is_dataclass
from inspect import cleandoc

from mashumaro.jsonschema.models import Context, JSONSchema
from mashumaro.jsonschema.schema import Instance


class BasePlugin:
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: JSONSchema | None = None,
    ) -> JSONSchema | None:
        pass


class DocstringDescriptionPlugin(BasePlugin):
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: JSONSchema | None = None,
    ) -> JSONSchema | None:
        if schema and is_dataclass(instance.type) and instance.type.__doc__:
            schema.description = cleandoc(instance.type.__doc__)
        return None
