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
    Deque,
    Dict,
    FrozenSet,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from uuid import UUID

import pytest
from typing_extensions import Annotated, Literal

from mashumaro.core.const import PEP_585_COMPATIBLE
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
    Pattern,
    UniqueItems,
)
from mashumaro.jsonschema.builder import build_json_schema
from mashumaro.jsonschema.models import (
    JSONArraySchema,
    JSONObjectSchema,
    JSONSchema,
    JSONSchemaInstanceFormatExtension,
    JSONSchemaInstanceType,
    JSONSchemaStringFormat,
)
from mashumaro.jsonschema.schema import EmptyJSONSchema
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
)
from tests.test_pep_655 import (
    TypedDictCorrectNotRequired,
    TypedDictCorrectRequired,
)


def test_jsonschema_for_dataclass():
    @dataclass
    class DataClass:
        a: int
        b: float = 3.14
        c: Optional[int] = field(default=None, metadata={"alias": "cc"})
        d: str = ""

        class Config:
            aliases = {"d": "dd"}

    assert build_json_schema(DataClass) == JSONObjectSchema(
        title="DataClass",
        properties={
            "a": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
            "b": JSONSchema(type=JSONSchemaInstanceType.NUMBER, default=3.14),
            "cc": JSONSchema(
                anyOf=[
                    JSONSchema(type=JSONSchemaInstanceType.INTEGER),
                    JSONSchema(type=JSONSchemaInstanceType.NULL),
                ],
                default=None,
            ),
            "dd": JSONSchema(type=JSONSchemaInstanceType.STRING, default=""),
        },
        additionalProperties=False,
        required=["a"],
    )
    assert build_json_schema(DataClass, all_refs=True) == JSONSchema(
        reference="#/defs/DataClass",
        definitions={
            "DataClass": JSONObjectSchema(
                title="DataClass",
                properties={
                    "a": JSONSchema(type=JSONSchemaInstanceType.INTEGER),
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
                },
                additionalProperties=False,
                required=["a"],
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
        ]
    ) == JSONSchema(
        type=instance_type,
        minimum=1,
        maximum=2,
        exclusiveMinimum=0,
        exclusiveMaximum=3,
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
    if PEP_585_COMPATIBLE:
        assert build_json_schema(list) == JSONArraySchema()


def test_jsonschema_for_deque():
    assert build_json_schema(Deque[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(Deque) == JSONArraySchema()
    assert build_json_schema(Deque[Any]) == JSONArraySchema()
    if PEP_585_COMPATIBLE:
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
    if PEP_585_COMPATIBLE:
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
    if PEP_585_COMPATIBLE:
        assert build_json_schema(frozenset) == JSONArraySchema(
            uniqueItems=True
        )
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


def test_jsonschema_for_mapping():
    for generic_type in (Dict, Mapping, MutableMapping):
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
    if PEP_585_COMPATIBLE:
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
