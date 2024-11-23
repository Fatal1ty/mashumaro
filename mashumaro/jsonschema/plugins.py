from dataclasses import is_dataclass
from inspect import cleandoc
from typing import Optional

from mashumaro.jsonschema.models import Context, JSONSchema
from mashumaro.jsonschema.schema import Instance


class BasePlugin:
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: Optional[JSONSchema] = None,
    ) -> Optional[JSONSchema]:
        pass


class DocstringDescriptionPlugin(BasePlugin):
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: Optional[JSONSchema] = None,
    ) -> Optional[JSONSchema]:
        if schema and is_dataclass(instance.type) and instance.type.__doc__:
            schema.description = cleandoc(instance.type.__doc__)
        return None
