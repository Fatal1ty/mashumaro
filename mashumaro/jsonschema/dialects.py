from dataclasses import dataclass


@dataclass(frozen=True)
class JSONSchemaDialect:
    definitions_root_pointer: str


@dataclass(frozen=True)
class JSONSchemaDraft202012Dialect(JSONSchemaDialect):
    definitions_root_pointer: str = "#/defs"


@dataclass(frozen=True)
class OpenAPI3Dialect(JSONSchemaDialect):
    definitions_root_pointer: str = "#/components/schemas"
    # TODO: There are more differences


jsonschema_draft_2020_12 = JSONSchemaDraft202012Dialect()
openapi_3 = OpenAPI3Dialect()


__all__ = [
    "JSONSchemaDialect",
    "jsonschema_draft_2020_12",
    "openapi_3",
]
