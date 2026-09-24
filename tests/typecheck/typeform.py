from typing import Any, Literal

from typing_extensions import TypedDict, assert_type

from mashumaro.codecs.basic import BasicDecoder, BasicEncoder
from mashumaro.codecs.basic import decode as basic_decode
from mashumaro.codecs.json import JSONDecoder, JSONEncoder, json_decode
from mashumaro.codecs.msgpack import MessagePackDecoder, MessagePackEncoder
from mashumaro.codecs.orjson import ORJSONDecoder, ORJSONEncoder
from mashumaro.codecs.toml import TOMLDecoder, TOMLEncoder
from mashumaro.codecs.yaml import YAMLDecoder, YAMLEncoder
from mashumaro.jsonschema import JSONSchemaBuilder, build_json_schema


class Payload(TypedDict):
    id: int
    name: str


def check_type_form_inference() -> None:
    assert_type(BasicDecoder(list[int]), BasicDecoder[list[int]])
    assert_type(BasicEncoder(list[int]), BasicEncoder[list[int]])
    assert_type(
        JSONDecoder(dict[str, Payload]), JSONDecoder[dict[str, Payload]]
    )
    assert_type(JSONEncoder(int | None), JSONEncoder[int | None])
    assert_type(YAMLDecoder(Payload), YAMLDecoder[Payload])
    assert_type(YAMLEncoder(Payload), YAMLEncoder[Payload])
    assert_type(
        MessagePackDecoder(tuple[int, ...]),
        MessagePackDecoder[tuple[int, ...]],
    )
    assert_type(
        MessagePackEncoder(tuple[int, ...]),
        MessagePackEncoder[tuple[int, ...]],
    )
    assert_type(TOMLDecoder(dict[str, int]), TOMLDecoder[dict[str, int]])
    assert_type(TOMLEncoder(dict[str, int]), TOMLEncoder[dict[str, int]])
    assert_type(
        ORJSONDecoder(Literal["a", "b"]), ORJSONDecoder[Literal["a", "b"]]
    )
    assert_type(ORJSONEncoder(Any), ORJSONEncoder[Any])
    assert_type(BasicDecoder(None), BasicDecoder[None])

    assert_type(basic_decode([], list[int]), list[int])
    assert_type(json_decode("null", int | None), int | None)

    build_json_schema(list[Payload])
    build_json_schema(Any)
    build_json_schema(None)
    JSONSchemaBuilder().build(dict[str, Payload])
