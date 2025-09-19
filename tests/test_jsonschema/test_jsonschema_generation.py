import collections
import datetime
import ipaddress
import os
from base64 import encodebytes
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import (
    Path,
    PosixPath,
    PurePath,
    PurePosixPath,
    PureWindowsPath,
    WindowsPath,
)
from typing import (
    AbstractSet,
    Any,
    ByteString,
    ChainMap,
    Counter,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Optional,
    OrderedDict,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from typing_extensions import Annotated, Literal, TypeVarTuple, Unpack

from mashumaro.config import BaseConfig
from mashumaro.core.meta.helpers import type_name
from mashumaro.helper import pass_through
from mashumaro.jsonschema.annotations import (
    Contains,
    DependentRequired,
    ExclusiveMaximum,
    ExclusiveMinimum,
    MaxContains,
    Maximum,
    MaxItems,
    MaxLength,
    MaxProperties,
    MinContains,
    Minimum,
    MinItems,
    MinLength,
    MinProperties,
    MultipleOf,
    Pattern,
    UniqueItems,
)
from mashumaro.jsonschema.builder import JSONSchemaBuilder, build_json_schema
from mashumaro.jsonschema.dialects import DRAFT_2020_12, OPEN_API_3_1
from mashumaro.jsonschema.models import (
    Context,
    JSONArraySchema,
    JSONObjectSchema,
    JSONSchema,
    JSONSchemaInstanceFormat,
    JSONSchemaInstanceFormatExtension,
    JSONSchemaInstanceType,
    JSONSchemaStringFormat,
)
from mashumaro.jsonschema.plugins import BasePlugin
from mashumaro.jsonschema.schema import (
    UTC_OFFSET_PATTERN,
    EmptyJSONSchema,
    Instance,
)
from mashumaro.types import Discriminator, SerializationStrategy
from tests.entities import (
    CustomPath,
    GenericNamedTuple,
    GenericTypedDict,
    MyDatetimeNewType,
    MyEnum,
    MyFlag,
    MyIntEnum,
    MyIntFlag,
    MyNamedTuple,
    MyNamedTupleWithDefaults,
    MyNamedTupleWithOptional,
    MyNativeStrEnum,
    MyStrEnum,
    MyUntypedNamedTuple,
    MyUntypedNamedTupleWithDefaults,
    T,
    T_Optional_int,
    TAny,
    TInt,
    TIntStr,
    TypedDictOptionalKeys,
    TypedDictOptionalKeysWithOptional,
    TypedDictRequiredAndOptionalKeys,
    TypedDictRequiredKeys,
    TypedDictRequiredKeysWithOptional,
    TypedDictWithReadOnly,
)
from tests.test_pep_655 import (
    TypedDictCorrectNotRequired,
    TypedDictCorrectRequired,
)

Ts = TypeVarTuple("Ts")


def dummy_serialize_as_str(_: Any) -> str:
    return "dummy"  # pragma: no cover


class ThirdPartyType:
    pass


@dataclass
class DataClassWithThirdPartyType:
    a: ThirdPartyType
    b: Optional[ThirdPartyType]
    c: ThirdPartyType = ThirdPartyType()
    d: Optional[ThirdPartyType] = None

    class Config(BaseConfig):
        serialization_strategy = {
            ThirdPartyType: {
                "deserialize": ThirdPartyType,
                "serialize": dummy_serialize_as_str,
            }
        }


def test_jsonschema_for_dataclass():
    @dataclass
    class MyClass:
        a: int
        b: float = 3.14
        c: Optional[int] = field(default=None, metadata={"alias": "cc"})
        d: str = ""
        e: int = field(init=False)
        f: List[int] = field(
            default_factory=list, metadata={"description": "description for f"}
        )

        class Config:
            aliases = {"a": "aa", "d": "dd"}

    assert build_json_schema(MyClass) == JSONObjectSchema(
        title="MyClass",
        properties={
            "aa": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "b": JSONSchema(type=JSONSchemaInstanceType.NUMBER, default=3.14),
            "cc": JSONSchema(
                anyOf=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NULL),
                ],
                default=None,
            ),
            "dd": JSONSchema(type=JSONSchemaInstanceType.STRING, default=""),
            "f": JSONArraySchema(
                items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                description="description for f",
            ),
        },
        additionalProperties=False,
        required=["aa"],
    )
    assert build_json_schema(MyClass, all_refs=True) == JSONSchema(
        reference="#/$defs/test_jsonschema_for_dataclass__locals__MyClass",
        definitions={
            "test_jsonschema_for_dataclass__locals__MyClass": JSONObjectSchema(
                title="test_jsonschema_for_dataclass__locals__MyClass",
                properties={
                    "aa": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    "b": JSONSchema(
                        type=JSONSchemaInstanceType.NUMBER, default=3.14
                    ),
                    "cc": JSONSchema(
                        anyOf=[
                            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                            JSONSchema(type=JSONSchemaInstanceType.NULL),
                        ],
                        default=None,
                    ),
                    "dd": JSONSchema(
                        type=JSONSchemaInstanceType.STRING, default=""
                    ),
                    "f": JSONArraySchema(
                        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                        description="description for f",
                    ),
                },
                additionalProperties=False,
                required=["aa"],
            )
        },
    )


def test_jsonschema_for_any():
    assert build_json_schema(Any) == EmptyJSONSchema()


def test_jsonschema_for_literal():
    assert build_json_schema(Literal[1]) == JSONSchema(const=1)
    assert build_json_schema(Literal[1, 2]) == JSONSchema(enum=[1, 2])
    assert build_json_schema(Literal["x", "y"]) == JSONSchema(enum=["x", "y"])
    assert build_json_schema(Literal[True, False]) == JSONSchema(
        enum=[True, False]
    )
    assert build_json_schema(Literal[1, None]) == JSONSchema(enum=[1, None])
    assert build_json_schema(Literal[MyEnum.a, MyEnum.b]) == JSONSchema(
        enum=["letter a", "letter b"]
    )
    assert build_json_schema(Literal[b"x", b"y"]) == JSONSchema(
        enum=[encodebytes(b"x").decode(), encodebytes(b"y").decode()]
    )


def test_jsonschema_for_special_typing_primitives():
    assert build_json_schema(Union[int, str]) == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.STRING),
        ]
    )
    assert build_json_schema(TAny) == EmptyJSONSchema()
    assert build_json_schema(T) == EmptyJSONSchema()
    assert build_json_schema(TInt) == JSONSchema(
        type=JSONSchemaInstanceType.INTEGER
    )
    assert build_json_schema(TIntStr) == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.STRING),
        ]
    )
    assert build_json_schema(T_Optional_int) == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.NULL),
        ]
    )
    assert build_json_schema(MyDatetimeNewType) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaStringFormat.DATETIME,
    )


@pytest.mark.parametrize(
    ("number_type", "instance_type"),
    (
        (int, JSONSchemaInstanceType.INTEGER),
        (float, JSONSchemaInstanceType.NUMBER),
    ),
)
def test_jsonschema_for_number(number_type, instance_type):
    assert build_json_schema(number_type) == JSONSchema(type=instance_type)
    assert build_json_schema(
        Annotated[
            number_type,
            Minimum(1),
            Maximum(2),
            ExclusiveMinimum(0),
            ExclusiveMaximum(3),
            MultipleOf(2),
        ]
    ) == JSONSchema(
        type=instance_type,
        minimum=1,
        maximum=2,
        exclusiveMinimum=0,
        exclusiveMaximum=3,
        multipleOf=2,
    )


def test_jsonschema_for_bool():
    assert build_json_schema(bool) == JSONSchema(
        type=JSONSchemaInstanceType.BOOLEAN
    )


def test_jsonschema_for_none():
    for instance_type in (None, type(None)):
        assert build_json_schema(instance_type) == JSONSchema(
            type=JSONSchemaInstanceType.NULL
        )


@pytest.mark.parametrize(
    ("instance_type", "string_format"),
    (
        (datetime.datetime, JSONSchemaStringFormat.DATETIME),
        (datetime.date, JSONSchemaStringFormat.DATE),
        (datetime.time, JSONSchemaStringFormat.TIME),
    ),
)
def test_jsonschema_for_datetime_objects(instance_type, string_format):
    assert build_json_schema(instance_type) == JSONSchema(
        type=JSONSchemaInstanceType.STRING, format=string_format
    )


def test_jsonschema_for_timedelta():
    assert build_json_schema(datetime.timedelta) == JSONSchema(
        type=JSONSchemaInstanceType.NUMBER,
        format=JSONSchemaInstanceFormatExtension.TIMEDELTA,
    )


def test_jsonschema_for_timezone():
    assert build_json_schema(datetime.timezone) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        pattern=UTC_OFFSET_PATTERN,
    )


def test_jsonschema_for_zone_info():
    assert build_json_schema(ZoneInfo) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaInstanceFormatExtension.TIME_ZONE,
    )


def test_jsonschema_for_uuid():
    assert build_json_schema(UUID) == JSONSchema(
        type=JSONSchemaInstanceType.STRING, format=JSONSchemaStringFormat.UUID
    )


@pytest.mark.parametrize(
    ("instance_type", "string_format"),
    (
        (ipaddress.IPv4Address, JSONSchemaStringFormat.IPV4ADDRESS),
        (ipaddress.IPv6Address, JSONSchemaStringFormat.IPV6ADDRESS),
        (ipaddress.IPv4Network, JSONSchemaInstanceFormatExtension.IPV4NETWORK),
        (ipaddress.IPv6Network, JSONSchemaInstanceFormatExtension.IPV6NETWORK),
        (ipaddress.IPv4Network, JSONSchemaInstanceFormatExtension.IPV4NETWORK),
        (ipaddress.IPv6Network, JSONSchemaInstanceFormatExtension.IPV6NETWORK),
    ),
)
def test_jsonschema_for_ipaddress(instance_type, string_format):
    assert build_json_schema(instance_type) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=string_format,
    )


def test_jsonschema_for_decimal():
    assert build_json_schema(Decimal) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaInstanceFormatExtension.DECIMAL,
    )


def test_jsonschema_for_fraction():
    assert build_json_schema(Fraction) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaInstanceFormatExtension.FRACTION,
    )


def test_jsonschema_for_bytestring():
    for instance_type in (ByteString, bytes, bytearray):
        assert build_json_schema(instance_type) == JSONSchema(
            type=JSONSchemaInstanceType.STRING,
            format=JSONSchemaInstanceFormatExtension.BASE64,
        )


def test_jsonschema_for_str():
    assert build_json_schema(str) == JSONSchema(
        type=JSONSchemaInstanceType.STRING
    )
    assert build_json_schema(
        Annotated[str, MinLength(1), MaxLength(5), Pattern("$[a-z]+^")]
    ) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        minLength=1,
        maxLength=5,
        pattern="$[a-z]+^",
    )


def test_jsonschema_for_list():
    assert build_json_schema(List[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
    assert build_json_schema(List) == JSONArraySchema()
    assert build_json_schema(List[Any]) == JSONArraySchema()
    assert build_json_schema(Annotated[List, min])
    assert build_json_schema(list) == JSONArraySchema()


def test_jsonschema_for_deque():
    assert build_json_schema(Deque[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(Deque) == JSONArraySchema()
    assert build_json_schema(Deque[Any]) == JSONArraySchema()
    assert build_json_schema(collections.deque) == JSONArraySchema()


def test_jsonschema_for_tuple():
    assert build_json_schema(Tuple[int]) == JSONArraySchema(
        prefixItems=[JSONSchema(type=JSONSchemaInstanceType.INTEGER)],
        maxItems=1,
        minItems=1,
    )
    assert build_json_schema(Tuple) == JSONArraySchema()
    assert build_json_schema(Tuple[()]) == JSONArraySchema(maxItems=0)
    assert build_json_schema(Tuple[Any]) == JSONArraySchema(
        prefixItems=[EmptyJSONSchema()], maxItems=1, minItems=1
    )
    assert build_json_schema(Tuple[Any, ...]) == JSONArraySchema()
    assert build_json_schema(Tuple[int, ...]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
    assert build_json_schema(tuple) == JSONArraySchema()


def test_jsonschema_for_named_tuple():
    assert build_json_schema(MyNamedTuple) == JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(MyNamedTupleWithDefaults) == JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER, default=1),
            JSONSchema(type=JSONSchemaInstanceType.NUMBER, default=2.0),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(MyNamedTupleWithOptional) == JSONArraySchema(
        prefixItems=[
            JSONSchema(
                anyOf=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NULL),
                ]
            ),
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(MyUntypedNamedTuple) == JSONArraySchema(
        prefixItems=[EmptyJSONSchema(), EmptyJSONSchema()],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(
        MyUntypedNamedTupleWithDefaults
    ) == JSONArraySchema(
        prefixItems=[JSONSchema(default=1), JSONSchema(default=2.0)],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(GenericNamedTuple) == JSONArraySchema(
        prefixItems=[
            EmptyJSONSchema(),
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(GenericNamedTuple[float]) == JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        ],
        maxItems=2,
        minItems=2,
    )


def test_jsonschema_for_named_tuple_as_dict():
    @dataclass
    class DataClassA:
        x: MyNamedTuple = field(metadata={"serialize": "as_dict"})

    @dataclass
    class DataClassB:
        x: MyNamedTuple

        class Config:
            namedtuple_as_dict = True

    schema = JSONObjectSchema(
        properties={
            "i": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "f": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        },
        additionalProperties=False,
        required=["i", "f"],
    )
    assert build_json_schema(DataClassA).properties["x"] == schema
    assert build_json_schema(DataClassB).properties["x"] == schema


def test_jsonschema_for_named_tuple_as_list():
    @dataclass
    class DataClassA:
        x: MyNamedTuple = field(metadata={"serialize": "as_list"})

    @dataclass
    class DataClassB:
        x: MyNamedTuple

        class Config:
            namedtuple_as_dict = False

    schema = JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(DataClassA).properties["x"] == schema
    assert build_json_schema(DataClassB).properties["x"] == schema


def test_jsonschema_for_named_tuple_with_overridden_serialization_method():
    class MySerializationStrategy(SerializationStrategy):
        def serialize(self, value: Any) -> MyNamedTuple: ...
        def deserialize(self, value: Any) -> Any: ...

    class MyAnySerializationStrategy(SerializationStrategy):
        def serialize(self, value: Any) -> Any: ...
        def deserialize(self, value: Any) -> Any: ...

    @dataclass
    class DataClassA:
        x: MyNamedTuple

        class Config:
            serialization_strategy = {MyNamedTuple: {"serialize": lambda x: x}}

    @dataclass
    class DataClassB:
        x: MyNamedTuple

        class Config:
            serialization_strategy = {
                MyNamedTuple: MyAnySerializationStrategy()
            }

    @dataclass
    class DataClassC:
        x: MyNamedTuple

        class Config:
            serialization_strategy = {MyNamedTuple: pass_through}

    @dataclass
    class DataClassD:
        x: MyNamedTuple

        class Config:
            serialization_strategy = {MyNamedTuple: MySerializationStrategy()}

    schema = JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(DataClassA).properties["x"] == EmptyJSONSchema()
    assert build_json_schema(DataClassB).properties["x"] == EmptyJSONSchema()
    assert build_json_schema(DataClassC).properties["x"] == schema
    assert build_json_schema(DataClassD).properties["x"] == schema


def test_jsonschema_for_set():
    for generic_type in (FrozenSet, AbstractSet):
        assert build_json_schema(generic_type[int]) == JSONArraySchema(
            items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            uniqueItems=True,
        )
        assert build_json_schema(generic_type) == JSONArraySchema(
            uniqueItems=True
        )
        assert build_json_schema(generic_type[Any]) == JSONArraySchema(
            uniqueItems=True
        )
    assert build_json_schema(frozenset) == JSONArraySchema(uniqueItems=True)
    assert build_json_schema(set) == JSONArraySchema(uniqueItems=True)


def test_jsonschema_for_chainmap():
    assert build_json_schema(ChainMap[str, int]) == JSONArraySchema(
        items=JSONObjectSchema(
            propertyNames=JSONSchema(type=JSONSchemaInstanceType.STRING),
            additionalProperties=JSONSchema(
                type=JSONSchemaInstanceType.INTEGER
            ),
        )
    )
    assert build_json_schema(ChainMap) == JSONArraySchema(
        items=JSONObjectSchema()
    )
    assert build_json_schema(ChainMap[Any, Any]) == JSONArraySchema(
        items=JSONObjectSchema()
    )


def test_jsonschema_for_counter():
    assert build_json_schema(Counter[str]) == JSONObjectSchema(
        additionalProperties=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        propertyNames=JSONSchema(type=JSONSchemaInstanceType.STRING),
    )
    assert build_json_schema(Counter) == JSONObjectSchema(
        additionalProperties=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
    assert build_json_schema(Counter[Any]) == JSONObjectSchema(
        additionalProperties=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(
        Annotated[
            Counter,
            MinProperties(1),
            MaxProperties(5),
            DependentRequired({"a": {"b"}, "b": {"c", "d"}}),
        ]
    ) == JSONObjectSchema(
        additionalProperties=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        minProperties=1,
        maxProperties=5,
        dependentRequired={"a": {"b"}, "b": {"c", "d"}},
    )


def test_jsonschema_for_typeddict():
    assert build_json_schema(TypedDictRequiredKeys) == JSONObjectSchema(
        properties={
            "int": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "float": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        },
        additionalProperties=False,
        required=["float", "int"],
    )
    assert build_json_schema(TypedDictOptionalKeys) == JSONObjectSchema(
        properties={
            "int": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "float": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        },
        additionalProperties=False,
    )
    assert build_json_schema(
        TypedDictRequiredAndOptionalKeys
    ) == JSONObjectSchema(
        properties={
            "int": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "float": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
            "str": JSONSchema(type=JSONSchemaInstanceType.STRING),
        },
        additionalProperties=False,
        required=["float", "int"],
    )
    assert build_json_schema(
        TypedDictRequiredKeysWithOptional
    ) == JSONObjectSchema(
        properties={
            "x": JSONSchema(
                anyOf=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NULL),
                ]
            ),
            "y": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["x", "y"],
    )
    assert build_json_schema(
        TypedDictOptionalKeysWithOptional
    ) == JSONObjectSchema(
        properties={
            "x": JSONSchema(
                anyOf=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NULL),
                ]
            ),
            "y": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
        },
        additionalProperties=False,
    )
    assert build_json_schema(GenericTypedDict) == JSONObjectSchema(
        properties={
            "x": EmptyJSONSchema(),
            "y": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["x", "y"],
    )
    assert build_json_schema(GenericTypedDict[float]) == JSONObjectSchema(
        properties={
            "x": JSONSchema(type=JSONSchemaInstanceType.NUMBER),
            "y": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["x", "y"],
    )
    assert build_json_schema(GenericTypedDict[Any]) == JSONObjectSchema(
        properties={
            "x": EmptyJSONSchema(),
            "y": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["x", "y"],
    )
    assert build_json_schema(TypedDictCorrectNotRequired) == JSONObjectSchema(
        properties={
            "required": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "not_required": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["required"],
    )
    assert build_json_schema(TypedDictCorrectRequired) == JSONObjectSchema(
        properties={
            "required": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "not_required": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=False,
        required=["required"],
    )
    assert build_json_schema(TypedDictWithReadOnly) == JSONObjectSchema(
        properties={"x": JSONSchema(type=JSONSchemaInstanceType.INTEGER)},
        additionalProperties=False,
        required=["x"],
    )


def test_jsonschema_for_mapping():
    for generic_type in (
        Dict,
        Mapping,
        MutableMapping,
        OrderedDict,
        DefaultDict,
    ):
        assert build_json_schema(generic_type[str, int]) == JSONObjectSchema(
            additionalProperties=JSONSchema(
                type=JSONSchemaInstanceType.INTEGER
            ),
            propertyNames=JSONSchema(type=JSONSchemaInstanceType.STRING),
        )
        assert build_json_schema(generic_type) == JSONObjectSchema()
        assert build_json_schema(generic_type[Any, Any]) == JSONObjectSchema()
        assert build_json_schema(
            Annotated[
                generic_type,
                MinProperties(1),
                MaxProperties(5),
                DependentRequired({"a": {"b"}, "b": {"c", "d"}}),
            ]
        ) == JSONObjectSchema(
            minProperties=1,
            maxProperties=5,
            dependentRequired={"a": {"b"}, "b": {"c", "d"}},
        )
    assert build_json_schema(
        DefaultDict[int, Dict[str, int]]
    ) == JSONObjectSchema(
        additionalProperties=JSONObjectSchema(
            additionalProperties=JSONSchema(
                type=JSONSchemaInstanceType.INTEGER,
            ),
            propertyNames=JSONSchema(type=JSONSchemaInstanceType.STRING),
        ),
        propertyNames=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(dict) == JSONObjectSchema()


def test_jsonschema_for_sequence():
    assert build_json_schema(Sequence[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
    assert build_json_schema(Sequence) == JSONArraySchema()
    assert build_json_schema(Sequence[Any]) == JSONArraySchema()


def test_jsonschema_for_pathlike():
    for pathlike_type in (
        Path,
        PurePath,
        PosixPath,
        PurePosixPath,
        WindowsPath,
        PureWindowsPath,
        os.PathLike,
        CustomPath,
    ):
        assert build_json_schema(pathlike_type) == JSONSchema(
            type=JSONSchemaInstanceType.STRING,
            format=JSONSchemaInstanceFormatExtension.PATH,
        )
    assert build_json_schema(
        Annotated[Path, MinLength(10), MaxLength(20)]
    ) == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaInstanceFormatExtension.PATH,
        minLength=10,
        maxLength=20,
    )


def test_jsonschema_for_array_like_with_constraints():
    for array_type in (List, Deque, Tuple, FrozenSet, AbstractSet):
        schema = build_json_schema(
            Annotated[array_type, MinItems(1), MaxItems(5)]
        )
        assert schema.minItems == 1
        assert schema.maxItems == 5

        schema = build_json_schema(Annotated[array_type, UniqueItems(True)])
        assert schema.uniqueItems

        schema = build_json_schema(Annotated[array_type, UniqueItems(False)])
        assert not schema.uniqueItems

        contains_schema = JSONSchema(type=JSONSchemaInstanceType.INTEGER)
        schema = build_json_schema(
            Annotated[array_type, Contains(contains_schema)]
        )
        assert schema.contains == contains_schema
        assert schema.minContains is None
        assert schema.maxContains is None

        schema = build_json_schema(
            Annotated[array_type, MinContains(1), MaxContains(2)]
        )
        assert schema.contains is None
        assert schema.minContains is None
        assert schema.maxContains is None

        schema = build_json_schema(
            Annotated[
                array_type,
                Contains(contains_schema),
                MinContains(1),
                MaxContains(2),
            ]
        )
        assert schema.contains == contains_schema
        assert schema.minContains == 1
        assert schema.maxContains == 2


def test_jsonschema_for_enum():
    assert build_json_schema(MyEnum) == JSONSchema(
        enum=["letter a", "letter b"]
    )
    assert build_json_schema(MyStrEnum) == JSONSchema(
        enum=["letter a", "letter b"]
    )
    assert build_json_schema(MyNativeStrEnum) == JSONSchema(
        enum=["letter a", "letter b"]
    )
    assert build_json_schema(MyIntEnum) == JSONSchema(enum=[1, 2])
    assert build_json_schema(MyFlag) == JSONSchema(enum=[1, 2])
    assert build_json_schema(MyIntFlag) == JSONSchema(enum=[1, 2])


def test_jsonschema_for_type_var_tuple():
    assert build_json_schema(Ts) == JSONArraySchema()
    assert build_json_schema(
        Tuple[Unpack[Tuple[float, str]]]
    ) == JSONArraySchema(
        prefixItems=[
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
            JSONSchema(type=JSONSchemaInstanceType.STRING),
        ],
        maxItems=2,
        minItems=2,
    )
    assert build_json_schema(
        Tuple[Tuple[Unpack[Tuple[float, ...]], str], int]
    ) == JSONArraySchema(
        prefixItems=[
            JSONArraySchema(minItems=1),
            JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        ],
        maxItems=2,
        minItems=2,
    )

    @dataclass
    class GenericDataClass(Generic[Unpack[Ts]]):
        x: Tuple[Unpack[Ts]]

    assert build_json_schema(
        GenericDataClass[Unpack[Tuple[int, float]], datetime.time]
    ) == JSONObjectSchema(
        title="GenericDataClass",
        properties={
            "x": JSONArraySchema(
                prefixItems=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NUMBER),
                    JSONSchema(
                        type=JSONSchemaInstanceType.STRING,
                        format=JSONSchemaStringFormat.TIME,
                    ),
                ],
                maxItems=3,
                minItems=3,
            )
        },
        additionalProperties=False,
        required=["x"],
    )


def test_jsonschema_for_unsupported_type():
    with pytest.raises(NotImplementedError):
        build_json_schema(object)


def test_overridden_serialization_method_without_signature():
    @dataclass
    class DataClass:
        x: datetime.datetime
        y: datetime.datetime = field(
            metadata={"serialize": datetime.datetime.timestamp}
        )

        class Config(BaseConfig):
            serialization_strategy = {
                datetime.datetime: {
                    "serialize": datetime.datetime.timestamp,
                }
            }

    with pytest.warns(
        UserWarning, match=f"Type Any will be used for {type_name(DataClass)}"
    ):
        assert (
            build_json_schema(DataClass).properties["x"] == EmptyJSONSchema()
        )
        assert (
            build_json_schema(DataClass).properties["y"] == EmptyJSONSchema()
        )


def test_overridden_serialization_method_without_return_annotation():
    def as_timestamp(dt: datetime.datetime):  # pragma: no cover
        return dt.timestamp()

    @dataclass
    class DataClass:
        x: datetime.datetime
        y: datetime.datetime = field(metadata={"serialize": as_timestamp})

        class Config(BaseConfig):
            serialization_strategy = {
                datetime.datetime: {"serialize": as_timestamp}
            }

    assert build_json_schema(DataClass).properties["x"] == EmptyJSONSchema()
    assert build_json_schema(DataClass).properties["y"] == EmptyJSONSchema()


def test_overridden_serialization_method_with_return_annotation():
    def as_timestamp(dt: datetime.datetime) -> float:
        return dt.timestamp()  # pragma: no cover

    def first_datetime_as_timestamp(
        seq: List[datetime.datetime],
    ) -> float:
        return as_timestamp(seq[0])  # pragma: no cover

    @dataclass
    class DataClass:
        a: datetime.datetime
        b: datetime.datetime = field(metadata={"serialize": as_timestamp})
        c: List[datetime.datetime]
        d: List[datetime.datetime] = field(
            metadata={"serialize": first_datetime_as_timestamp}
        )
        e: Optional[datetime.datetime]
        f: List[Optional[datetime.datetime]]

        class Config(BaseConfig):
            serialization_strategy = {
                datetime.datetime: {"serialize": as_timestamp}
            }

    schema = build_json_schema(DataClass)
    assert schema.properties["a"] == JSONSchema(
        type=JSONSchemaInstanceType.NUMBER
    )
    assert schema.properties["b"] == JSONSchema(
        type=JSONSchemaInstanceType.NUMBER
    )
    assert schema.properties["c"] == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.NUMBER)
    )
    assert schema.properties["d"] == JSONSchema(
        type=JSONSchemaInstanceType.NUMBER
    )
    assert schema.properties["e"] == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.NUMBER),
            JSONSchema(type=JSONSchemaInstanceType.NULL),
        ]
    )
    assert schema.properties["f"] == JSONArraySchema(
        items=JSONSchema(
            anyOf=[
                JSONSchema(type=JSONSchemaInstanceType.NUMBER),
                JSONSchema(type=JSONSchemaInstanceType.NULL),
            ]
        )
    )


@pytest.mark.parametrize(
    ("basic_type", "schema_type"),
    (
        (str, JSONSchemaInstanceType.STRING),
        (int, JSONSchemaInstanceType.INTEGER),
        (float, JSONSchemaInstanceType.NUMBER),
        (bool, JSONSchemaInstanceType.BOOLEAN),
    ),
)
def test_basic_type_as_overridden_serialization_method(
    basic_type, schema_type
):
    @dataclass
    class DataClass:
        x: ThirdPartyType
        y: List[ThirdPartyType]

        class Config(BaseConfig):
            serialization_strategy = {
                ThirdPartyType: {"serialize": basic_type}
            }

    assert build_json_schema(DataClass).properties["x"] == JSONSchema(
        type=schema_type
    )
    assert build_json_schema(DataClass).properties["y"] == JSONArraySchema(
        items=JSONSchema(type=schema_type)
    )


def test_dataclass_overridden_serialization_method():
    def serialize_as_str(value: Any) -> str:
        return str(value)  # pragma: no cover

    @dataclass
    class Inner:
        x: int

    @dataclass
    class DataClass:
        a: Inner
        b: Optional[Inner]
        c: List[Inner]
        d: List[Optional[Inner]]

        class Config(BaseConfig):
            serialization_strategy = {Inner: {"serialize": serialize_as_str}}

    schema = build_json_schema(DataClass)
    assert schema.properties["a"] == JSONSchema(
        type=JSONSchemaInstanceType.STRING
    )
    assert schema.properties["b"] == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.STRING),
            JSONSchema(type=JSONSchemaInstanceType.NULL),
        ]
    )
    assert schema.properties["c"] == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.STRING)
    )
    assert schema.properties["d"] == JSONArraySchema(
        items=JSONSchema(
            anyOf=[
                JSONSchema(type=JSONSchemaInstanceType.STRING),
                JSONSchema(type=JSONSchemaInstanceType.NULL),
            ]
        )
    )


def test_third_party_overridden_serialization_method():
    schema = build_json_schema(DataClassWithThirdPartyType)
    assert schema.properties["a"] == JSONSchema(
        type=JSONSchemaInstanceType.STRING
    )
    assert schema.properties["b"] == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.STRING),
            JSONSchema(type=JSONSchemaInstanceType.NULL),
        ]
    )
    assert schema.properties["c"] == JSONSchema(
        type=JSONSchemaInstanceType.STRING, default="dummy"
    )
    assert schema.properties["d"] == JSONSchema(
        anyOf=[
            JSONSchema(type=JSONSchemaInstanceType.STRING),
            JSONSchema(type=JSONSchemaInstanceType.NULL),
        ],
        default=None,
    )


def test_jsonschema_with_override_for_properties():
    @dataclass
    class DataClass:
        x: str
        y: datetime.datetime

        class Config(BaseConfig):
            json_schema = {
                "properties": {
                    "x": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Description for x",
                    },
                    "y": {
                        "type": "number",
                        "description": "Description for y",
                    },
                }
            }

    assert build_json_schema(DataClass).properties["x"] == JSONSchema(
        type=JSONSchemaInstanceType.STRING,
        format=JSONSchemaStringFormat.DATETIME,
        description="Description for x",
    )
    assert build_json_schema(DataClass).properties["y"] == JSONSchema(
        type=JSONSchemaInstanceType.NUMBER,
        description="Description for y",
    )


def test_jsonschema_with_dialect_uri():
    schema = build_json_schema(str, with_dialect_uri=True)
    assert schema.schema == DRAFT_2020_12.uri
    assert schema.to_dict()["$schema"] == DRAFT_2020_12.uri
    schema = build_json_schema(
        str, dialect=OPEN_API_3_1, with_dialect_uri=True
    )
    assert schema.schema == OPEN_API_3_1.uri
    assert schema.to_dict()["$schema"] == OPEN_API_3_1.uri


def test_jsonschema_with_ref_prefix():
    @dataclass
    class DataClass:
        pass

    schema = {
        "$ref": (
            "#/components/responses/"
            "test_jsonschema_with_ref_prefix__locals__DataClass"
        )
    }
    assert (
        build_json_schema(
            List[DataClass], all_refs=True, ref_prefix="#/components/responses"
        ).items.to_dict()
        == schema
    )
    assert (
        build_json_schema(
            List[DataClass],
            all_refs=True,
            ref_prefix="#/components/responses/",
        ).items.to_dict()
        == schema
    )
    assert (
        build_json_schema(
            List[DataClass],
            dialect=OPEN_API_3_1,
            ref_prefix="#/components/responses/",
        ).items.to_dict()
        == schema
    )

    assert (
        JSONSchemaBuilder(all_refs=True, ref_prefix="#/components/responses")
        .build(List[DataClass])
        .items.to_dict()
        == schema
    )
    assert (
        JSONSchemaBuilder(
            dialect=OPEN_API_3_1, ref_prefix="#/components/responses"
        )
        .build(List[DataClass])
        .items.to_dict()
        == schema
    )


def test_jsonschema_with_additional_properties_true():
    @dataclass
    class DataClass:
        x: int

        class Config(BaseConfig):
            json_schema = {"additionalProperties": True}

    schema = JSONObjectSchema(
        title="DataClass",
        properties={
            "x": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=True,
        required=["x"],
    )
    assert build_json_schema(DataClass) == schema


def test_jsonschema_with_additional_properties_schema():
    @dataclass
    class DataClass:
        x: int

        class Config(BaseConfig):
            json_schema = {
                "additionalProperties": JSONSchema(
                    type=JSONSchemaInstanceType.INTEGER
                )
            }

    schema = JSONObjectSchema(
        title="DataClass",
        properties={
            "x": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        },
        additionalProperties=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
        required=["x"],
    )
    assert build_json_schema(DataClass) == schema


def test_jsonschema_with_discriminator_for_local_types():
    @dataclass
    class A:
        value = "a"

    @dataclass
    class B:
        value = "b"

    @dataclass
    class Main:
        value: Annotated[
            Union[A, B], Discriminator(field="value", include_supertypes=True)
        ]

    schema = JSONObjectSchema(
        title="Main",
        properties={
            "value": JSONSchema(
                anyOf=[
                    JSONObjectSchema(
                        type=JSONSchemaInstanceType.OBJECT,
                        title="A",
                        additionalProperties=False,
                    ),
                    JSONObjectSchema(
                        type=JSONSchemaInstanceType.OBJECT,
                        title="B",
                        additionalProperties=False,
                    ),
                ],
            ),
        },
        additionalProperties=False,
        required=["value"],
    )
    assert build_json_schema(Main) == schema


def test_jsonschema_with_discriminator_with_default_for_local_types():
    @dataclass
    class A:
        value = "a"

    @dataclass
    class B:
        value = "b"

    @dataclass
    class Main:
        value: Annotated[
            Union[A, B, None],
            Discriminator(field="value", include_supertypes=True),
        ] = None

    schema = JSONObjectSchema(
        title="Main",
        properties={
            "value": JSONSchema(
                anyOf=[
                    JSONObjectSchema(
                        type=JSONSchemaInstanceType.OBJECT,
                        title="A",
                        additionalProperties=False,
                    ),
                    JSONObjectSchema(
                        type=JSONSchemaInstanceType.OBJECT,
                        title="B",
                        additionalProperties=False,
                    ),
                    JSONSchema(
                        type=JSONSchemaInstanceType.NULL,
                    ),
                ],
                default=None,
            ),
        },
        additionalProperties=False,
    )
    assert build_json_schema(Main) == schema


def test_jsonschema_with_optional_discriminator_and_default_for_local_types():
    @dataclass
    class A:
        value = "a"

    @dataclass
    class B:
        value = "b"

    @dataclass
    class Main:
        value: Optional[
            Annotated[
                Union[A, B],
                Discriminator(field="value", include_supertypes=True),
            ]
        ] = None

    schema = JSONObjectSchema(
        title="Main",
        properties={
            "value": JSONSchema(
                anyOf=[
                    JSONSchema(
                        anyOf=[
                            JSONObjectSchema(
                                type=JSONSchemaInstanceType.OBJECT,
                                title="A",
                                additionalProperties=False,
                            ),
                            JSONObjectSchema(
                                type=JSONSchemaInstanceType.OBJECT,
                                title="B",
                                additionalProperties=False,
                            ),
                        ]
                    ),
                    JSONSchema(
                        type=JSONSchemaInstanceType.NULL,
                    ),
                ],
                default=None,
            ),
        },
        additionalProperties=False,
    )
    assert build_json_schema(Main) == schema


def test_jsonschema_with_custom_instance_format():
    class CustomJSONSchemaInstanceFormatPlugin(BasePlugin):
        def get_schema(
            self,
            instance: Instance,
            ctx: Context,
            schema: Optional[JSONSchema] = None,
        ) -> Optional[JSONSchema]:
            for annotation in instance.annotations:
                if isinstance(annotation, JSONSchemaInstanceFormat):
                    schema.format = annotation
            return schema

    class Custom1InstanceFormat(JSONSchemaInstanceFormat):
        CUSTOM1 = "custom1"

    class CustomInstanceFormatBase(JSONSchemaInstanceFormat):
        pass

    class Custom2InstanceFormat(CustomInstanceFormatBase):
        CUSTOM2 = "custom2"

    type1 = Annotated[str, Custom1InstanceFormat.CUSTOM1]
    schema1 = build_json_schema(
        type1, plugins=[CustomJSONSchemaInstanceFormatPlugin()]
    )
    assert schema1.format is Custom1InstanceFormat.CUSTOM1
    assert schema1.to_dict()["format"] == "custom1"

    type2 = Annotated[int, Custom2InstanceFormat.CUSTOM2]
    schema2 = build_json_schema(
        type2, plugins=[CustomJSONSchemaInstanceFormatPlugin()]
    )
    assert schema2.format is Custom2InstanceFormat.CUSTOM2
    assert schema2.to_dict()["format"] == "custom2"

    assert (
        JSONSchema.from_dict({"format": "custom1"}).format
        is Custom1InstanceFormat.CUSTOM1
    )
    assert (
        JSONSchema.from_dict({"format": "custom2"}).format
        is Custom2InstanceFormat.CUSTOM2
    )

    @dataclass
    class MyClass:
        x: str
        y: str

        class Config(BaseConfig):
            json_schema = {
                "properties": {
                    "x": {"type": "string", "format": "custom1"},
                    "y": {"type": "string", "format": "custom2"},
                }
            }

    schema3 = build_json_schema(MyClass)
    assert schema3 == JSONObjectSchema(
        title="MyClass",
        properties={
            "x": JSONSchema(
                type=JSONSchemaInstanceType.STRING,
                format=Custom1InstanceFormat.CUSTOM1,
            ),
            "y": JSONSchema(
                type=JSONSchemaInstanceType.STRING,
                format=Custom2InstanceFormat.CUSTOM2,
            ),
        },
        required=["x", "y"],
        additionalProperties=False,
    )


def test_jsonschema_for_generic_dataclass():
    T = TypeVar("T")

    @dataclass
    class MyClass(Generic[T]):
        x: T
        y: list[T]

    assert build_json_schema(MyClass) == JSONObjectSchema(
        title="MyClass",
        properties={
            "x": EmptyJSONSchema(),
            "y": JSONArraySchema(),
        },
        additionalProperties=False,
        required=["x", "y"],
    )
    assert build_json_schema(MyClass[int]) == JSONObjectSchema(
        title="MyClass",
        properties={
            "x": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "y": JSONArraySchema(
                items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
            ),
        },
        additionalProperties=False,
        required=["x", "y"],
    )

    @dataclass
    class MyClass2(Generic[T]):
        z: MyClass[T]

    assert build_json_schema(MyClass2) == JSONObjectSchema(
        title="MyClass2",
        properties={
            "z": JSONObjectSchema(
                title="MyClass",
                properties={
                    "x": EmptyJSONSchema(),
                    "y": JSONArraySchema(),
                },
                additionalProperties=False,
                required=["x", "y"],
            )
        },
        additionalProperties=False,
        required=["z"],
    )
    assert build_json_schema(MyClass2[str]) == JSONObjectSchema(
        title="MyClass2",
        properties={
            "z": JSONObjectSchema(
                title="MyClass",
                properties={
                    "x": JSONSchema(type=JSONSchemaInstanceType.STRING),
                    "y": JSONArraySchema(
                        items=JSONSchema(type=JSONSchemaInstanceType.STRING)
                    ),
                },
                additionalProperties=False,
                required=["x", "y"],
            )
        },
        additionalProperties=False,
        required=["z"],
    )
