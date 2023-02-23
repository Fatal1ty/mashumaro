import datetime
import ipaddress
from dataclasses import MISSING, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from mashumaro.config import BaseConfig
from mashumaro.jsonschema.dialects import (
    JSONSchemaDialect,
    jsonschema_draft_2020_12,
)

try:
    from mashumaro.mixins.orjson import (
        DataClassORJSONMixin as DataClassJSONMixin,
    )
except ImportError:
    from mashumaro.mixins.json import DataClassJSONMixin  # type: ignore


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


@dataclass
class JSONSchema(DataClassJSONMixin):
    # common fields
    type: Optional[JSONSchemaInstanceType] = None
    enum: Optional[List[Any]] = None
    format: Optional[JSONSchemaInstanceFormat] = None
    title: Optional[str] = None
    description: Optional[str] = None
    anyOf: Optional[List["JSONSchema"]] = None
    reference: Optional[str] = None
    definitions: Optional[Dict[str, "JSONSchema"]] = None
    default: Optional[Any] = field(default_factory=lambda: MISSING)
    # JSONObjectSchema fields
    properties: Optional[Dict[str, "JSONSchema"]] = None
    patternProperties: Optional[Dict[str, "JSONSchema"]] = None
    additionalProperties: Optional["JSONSchema"] = None
    propertyNames: Optional["JSONSchema"] = None
    required: Optional[List[str]] = None
    # JSONArraySchema fields
    prefixItems: Optional[List["JSONSchema"]] = None
    items: Optional["JSONSchema"] = None
    maxItems: Optional[int] = None
    minItems: Optional[int] = None
    uniqueItems: Optional[bool] = None

    class Config(BaseConfig):
        omit_none = True
        serialize_by_alias = True
        aliases = {
            "reference": "$ref",
            "definitions": "$defs",
        }

    def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        if d.get("default") is MISSING:
            d.pop("default")
        return d


@dataclass
class JSONObjectSchema(JSONSchema):
    type: JSONSchemaInstanceType = JSONSchemaInstanceType.OBJECT


@dataclass
class JSONArraySchema(JSONSchema):
    type: JSONSchemaInstanceType = JSONSchemaInstanceType.ARRAY


@dataclass
class Context:
    dialect: JSONSchemaDialect = jsonschema_draft_2020_12
    definitions: Dict[str, JSONSchema] = field(default_factory=dict)
