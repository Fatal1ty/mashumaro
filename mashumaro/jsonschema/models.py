import datetime
import ipaddress
from collections.abc import Sequence
from dataclasses import MISSING, dataclass, field
from enum import Enum
from typing import Any, Dict, List

from typing_extensions import TYPE_CHECKING, Self, TypeAlias

from mashumaro.config import BaseConfig
from mashumaro.core.meta.helpers import iter_all_subclasses
from mashumaro.helper import pass_through
from mashumaro.jsonschema.dialects import DRAFT_2020_12, JSONSchemaDialect

if TYPE_CHECKING:  # pragma: no cover
    from mashumaro.jsonschema.plugins import BasePlugin
else:
    BasePlugin = Any

try:
    from mashumaro.mixins.orjson import (
        DataClassORJSONMixin as DataClassJSONMixin,
    )
except ImportError:  # pragma: no cover
    from mashumaro.mixins.json import DataClassJSONMixin  # type: ignore


# https://github.com/python/mypy/issues/3186
Number: TypeAlias = int | float

Null = object()


class JSONSchemaInstanceType(Enum):
    NULL = "null"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NUMBER = "number"
    STRING = "string"
    INTEGER = "integer"


class JSONSchemaInstanceFormat(Enum):
    pass


class JSONSchemaStringFormat(JSONSchemaInstanceFormat):
    DATETIME = "date-time"
    DATE = "date"
    TIME = "time"
    DURATION = "duration"
    EMAIL = "email"
    IDN_EMAIL = "idn-email"
    HOSTNAME = "hostname"
    IDN_HOSTNAME = "idn-hostname"
    IPV4ADDRESS = "ipv4"
    IPV6ADDRESS = "ipv6"
    URI = "uri"
    URI_REFERENCE = "uri-reference"
    IRI = "iri"
    IRI_REFERENCE = "iri-reference"
    UUID = "uuid"
    URI_TEMPLATE = "uri-template"
    JSON_POINTER = "json-pointer"
    RELATIVE_JSON_POINTER = "relative-json-pointer"
    REGEX = "regex"


class JSONSchemaInstanceFormatExtension(JSONSchemaInstanceFormat):
    TIMEDELTA = "time-delta"
    TIME_ZONE = "time-zone"
    IPV4NETWORK = "ipv4network"
    IPV6NETWORK = "ipv6network"
    IPV4INTERFACE = "ipv4interface"
    IPV6INTERFACE = "ipv6interface"
    DECIMAL = "decimal"
    FRACTION = "fraction"
    BASE64 = "base64"
    PATH = "path"


DATETIME_FORMATS = {
    datetime.datetime: JSONSchemaStringFormat.DATETIME,
    datetime.date: JSONSchemaStringFormat.DATE,
    datetime.time: JSONSchemaStringFormat.TIME,
}


IPADDRESS_FORMATS = {
    ipaddress.IPv4Address: JSONSchemaStringFormat.IPV4ADDRESS,
    ipaddress.IPv6Address: JSONSchemaStringFormat.IPV6ADDRESS,
    ipaddress.IPv4Network: JSONSchemaInstanceFormatExtension.IPV4NETWORK,
    ipaddress.IPv6Network: JSONSchemaInstanceFormatExtension.IPV6NETWORK,
    ipaddress.IPv4Interface: JSONSchemaInstanceFormatExtension.IPV4INTERFACE,
    ipaddress.IPv6Interface: JSONSchemaInstanceFormatExtension.IPV6INTERFACE,
}


def _deserialize_json_schema_instance_format(
    value: Any,
) -> JSONSchemaInstanceFormat:
    for cls in iter_all_subclasses(JSONSchemaInstanceFormat):
        try:
            return cls(value)
        except (ValueError, TypeError):
            pass
    raise ValueError(value)


@dataclass(unsafe_hash=True)
class JSONSchema(DataClassJSONMixin):
    # Common keywords
    schema: str | None = None
    type: JSONSchemaInstanceType | None = None
    enum: list[Any] | None = None
    const: Any | None = field(default_factory=lambda: MISSING)
    format: JSONSchemaInstanceFormat | None = None
    title: str | None = None
    description: str | None = None
    anyOf: List["JSONSchema"] | None = None
    reference: str | None = None
    definitions: Dict[str, "JSONSchema"] | None = None
    default: Any | None = field(default_factory=lambda: MISSING)
    deprecated: bool | None = None
    examples: list[Any] | None = None
    # Keywords for Objects
    properties: Dict[str, "JSONSchema"] | None = None
    patternProperties: Dict[str, "JSONSchema"] | None = None
    additionalProperties: "JSONSchema | bool | None" = None
    propertyNames: "JSONSchema | None" = None
    # Keywords for Arrays
    prefixItems: List["JSONSchema"] | None = None
    items: "JSONSchema | None" = None
    contains: "JSONSchema | None" = None
    # Validation keywords for numeric instances
    multipleOf: Number | None = None
    maximum: Number | None = None
    exclusiveMaximum: Number | None = None
    minimum: Number | None = None
    exclusiveMinimum: Number | None = None
    # Validation keywords for Strings
    maxLength: int | None = None
    minLength: int | None = None
    pattern: str | None = None
    # Validation keywords for Arrays
    maxItems: int | None = None
    minItems: int | None = None
    uniqueItems: bool | None = None
    maxContains: int | None = None
    minContains: int | None = None
    # Validation keywords for Objects
    maxProperties: int | None = None
    minProperties: int | None = None
    required: list[str] | None = None
    dependentRequired: dict[str, set[str]] | None = None

    class Config(BaseConfig):
        omit_none = True
        serialize_by_alias = True
        aliases = {
            "schema": "$schema",
            "reference": "$ref",
            "definitions": "$defs",
        }
        serialization_strategy = {
            int: pass_through,
            float: pass_through,
            Null: pass_through,
            JSONSchemaInstanceFormat: {
                "deserialize": _deserialize_json_schema_instance_format
            },
        }

    def __pre_serialize__(self) -> Self:
        if self.const is None:
            self.const = Null
        if self.default is None:
            self.default = Null
        return self

    def __post_serialize__(self, d: dict[Any, Any]) -> dict[Any, Any]:
        const = d.get("const")
        if const is MISSING:
            d.pop("const")
        elif const is Null:
            d["const"] = None
        default = d.get("default")
        if default is MISSING:
            d.pop("default")
        elif default is Null:
            d["default"] = None
        return d


@dataclass
class JSONObjectSchema(JSONSchema):
    type: JSONSchemaInstanceType | None = JSONSchemaInstanceType.OBJECT


@dataclass
class JSONArraySchema(JSONSchema):
    type: JSONSchemaInstanceType | None = JSONSchemaInstanceType.ARRAY


@dataclass
class Context:
    dialect: JSONSchemaDialect = DRAFT_2020_12
    definitions: dict[str, JSONSchema] = field(default_factory=dict)
    all_refs: bool | None = None
    ref_prefix: str | None = None
    plugins: Sequence[BasePlugin] = ()
    # PEP 695 TypeAliasType recursion guard
    _building_type_aliases: set[int] = field(default_factory=set, repr=False)
    # Dataclass recursion guard (e.g. typing.Self, direct or mutual references)
    _building_dataclasses: set[type] = field(default_factory=set, repr=False)
