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
    Sequence,
    Tuple,
)

from typing_extensions import Annotated

from mashumaro.jsonschema.annotations import MaxLength, MinLength, Pattern
from mashumaro.jsonschema.builder import build_json_schema
from mashumaro.jsonschema.models import (
    JSONArraySchema,
    JSONObjectSchema,
    JSONSchema,
    JSONSchemaInstanceFormatExtension,
    JSONSchemaInstanceType,
)
from mashumaro.jsonschema.schema import EmptyJSONSchema
from tests.entities import (
    GenericNamedTuple,
    MyNamedTuple,
    MyNamedTupleWithDefaults,
    MyNamedTupleWithOptional,
    MyUntypedNamedTuple,
    MyUntypedNamedTupleWithDefaults,
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


def test_jsonschema_for_deque():
    assert build_json_schema(Deque[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER),
    )
    assert build_json_schema(Deque) == JSONArraySchema()
    assert build_json_schema(Deque[Any]) == JSONArraySchema()


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
    assert build_json_schema(frozenset) == JSONArraySchema(uniqueItems=True)
    assert build_json_schema(set) == JSONArraySchema(uniqueItems=True)
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


def test_jsonschema_for_sequence():
    assert build_json_schema(Sequence[int]) == JSONArraySchema(
        items=JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    )
    assert build_json_schema(Sequence) == JSONArraySchema()
    assert build_json_schema(Sequence[Any]) == JSONArraySchema()
