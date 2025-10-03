from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import msgpack
import orjson
import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.exceptions import UnresolvedTypeReferenceError
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import SerializationStrategy

from .conftest import add_unpack_method


@dataclass
class A(DataClassDictMixin):
    x: B


@dataclass
class B(DataClassDictMixin):
    x: int


@dataclass
class Base(DataClassDictMixin):
    pass


@dataclass
class A1(Base):
    a: B1


@dataclass
class A2(Base):
    a: B2


@dataclass
class A3(Base):
    a: B1
    x: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class B1(Base):
    b: int


@dataclass
class AMessagePack(DataClassMessagePackMixin):
    x: BMessagePack


@dataclass
class BMessagePack(DataClassMessagePackMixin):
    x: int


@dataclass
class BaseMessagePack(DataClassMessagePackMixin):
    pass


@dataclass
class A1MessagePack(BaseMessagePack):
    a: B1MessagePack


@dataclass
class A2MessagePack(BaseMessagePack):
    a: B2


@dataclass
class A3MessagePack(BaseMessagePack):
    a: B1MessagePack
    x: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class B1MessagePack(BaseMessagePack):
    b: int


@dataclass
class A3ORJSON(DataClassORJSONMixin):
    a: B1ORJSON
    x: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class B1ORJSON(DataClassORJSONMixin):
    b: int


def test_postponed_annotation_evaluation():
    obj = A(x=B(x=1))
    assert obj.to_dict() == {"x": {"x": 1}}
    assert A.from_dict({"x": {"x": 1}}) == obj


def test_unresolved_type_with_allowed_postponed_annotation_evaluation():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: X

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass.from_dict({})

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass(x=1).to_dict()


def test_unresolved_type_with_disallowed_postponed_annotation_evaluation():
    with pytest.raises(UnresolvedTypeReferenceError):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: X

            class Config(BaseConfig):
                allow_postponed_evaluation = False

    with add_unpack_method:
        with pytest.raises(UnresolvedTypeReferenceError):

            @dataclass
            class DataClass(DataClassDictMixin):
                x: X

                class Config(BaseConfig):
                    allow_postponed_evaluation = False


def test_postponed_annotation_evaluation_with_parent():
    obj = A1(B1(1))
    assert A1.from_dict({"a": {"b": 1}}) == obj
    assert obj.to_dict() == {"a": {"b": 1}}


def test_postponed_annotation_evaluation_with_parent_and_no_reference():
    with pytest.raises(UnresolvedTypeReferenceError):
        A2.from_dict({"a": {"b": 1}})
    with pytest.raises(UnresolvedTypeReferenceError):
        A2(None).to_dict()


def test_postponed_annotation_evaluation_with_parent_and_dialect():
    class MyDialect(Dialect):
        serialization_strategy = {
            int: {
                "serialize": lambda i: str(int(i * 1000)),
                "deserialize": lambda s: int(int(s) / 1000),
            }
        }

    obj = A3(B1(1), 2)
    assert A3.from_dict({"a": {"b": 1}, "x": 2}) == obj
    assert A3.from_dict({"a": {"b": 1}, "x": "2000"}, dialect=MyDialect) == obj
    assert obj.to_dict() == {"a": {"b": 1}, "x": 2}
    assert obj.to_dict(dialect=MyDialect) == {"a": {"b": 1}, "x": "2000"}


def test_postponed_annotation_evaluation_msgpack():
    obj = AMessagePack(x=BMessagePack(x=1))
    assert obj.to_dict() == {"x": {"x": 1}}
    assert AMessagePack.from_dict({"x": {"x": 1}}) == obj
    dump = msgpack.dumps({"x": {"x": 1}})
    assert obj.to_msgpack() == dump
    assert AMessagePack.from_msgpack(dump) == obj


def test_unresolved_type_with_allowed_postponed_annotation_evaluation_msgpack():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: X

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass.from_msgpack(b"")

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass(x=1).to_msgpack()


def test_postponed_annotation_evaluation_with_parent_msgpack():
    obj = A1MessagePack(B1MessagePack(1))
    dump = msgpack.dumps({"a": {"b": 1}})
    assert A1MessagePack.from_msgpack(dump) == obj
    assert obj.to_msgpack() == dump


def test_postponed_annotation_evaluation_with_parent_and_no_reference_msgpack():
    with pytest.raises(UnresolvedTypeReferenceError):
        A2MessagePack.from_msgpack(b"")
    with pytest.raises(UnresolvedTypeReferenceError):
        A2MessagePack(None).to_msgpack()


def test_postponed_annotation_evaluation_with_parent_and_dialect_msgpack():
    class MyDialect(Dialect):
        serialization_strategy = {
            int: {
                "serialize": lambda i: str(int(i * 1000)),
                "deserialize": lambda s: int(int(s) / 1000),
            }
        }

    obj = A3MessagePack(B1MessagePack(1), 2)
    dump = msgpack.dumps({"a": {"b": 1}, "x": 2})
    dump_dialect = msgpack.dumps({"a": {"b": 1}, "x": "2000"})
    assert A3MessagePack.from_msgpack(dump) == obj
    assert A3MessagePack.from_msgpack(dump_dialect, dialect=MyDialect) == obj
    assert obj.to_msgpack() == dump
    assert obj.to_msgpack(dialect=MyDialect) == dump_dialect


def test_postponed_msgpack_with_custom_encoder_and_decoder():
    def decoder(data) -> Dict[str, bytes]:
        def modify(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = modify(v)
                else:
                    result[k] = v // 1000
            return result

        return modify(msgpack.loads(data))

    def encoder(data: Dict[str, bytes]) -> bytes:
        def modify(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = modify(v)
                else:
                    result[k] = v * 1000
            return result

        return msgpack.dumps(modify(data))

    instance = A3MessagePack(B1MessagePack(123), 456)
    dumped = msgpack.packb({"a": {"b": 123000}, "x": 456000})
    assert instance.to_msgpack(encoder=encoder) == dumped
    assert A3MessagePack.from_msgpack(dumped, decoder=decoder) == instance


def test_postponed_orjson_with_custom_encoder_and_decoder():
    def decoder(data) -> Dict[str, bytes]:
        def modify(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = modify(v)
                else:
                    result[k] = v // 1000
            return result

        return modify(orjson.loads(data))

    def encoder(data: Dict[str, bytes], **_) -> bytes:
        def modify(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = modify(v)
                else:
                    result[k] = v * 1000
            return result

        return orjson.dumps(modify(data))

    instance = A3ORJSON(B1ORJSON(123), 456)
    dumped = orjson.dumps({"a": {"b": 123000}, "x": 456000})
    assert instance.to_jsonb(encoder=encoder) == dumped
    assert A3ORJSON.from_json(dumped, decoder=decoder) == instance


def test_postponed_serialization_strategy() -> None:
    class Strategy(SerializationStrategy, use_annotations=True):
        def serialize(self, value) -> dict[str, Any]:
            return {"a": value}

        def deserialize(self, value: dict[str, Any]):
            return value.get("a")

    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: Optional[int]

        class Config(BaseConfig):
            serialization_strategy = {int: Strategy()}

    obj = MyDataClass(x=2)
    assert obj.to_dict() == {"x": {"a": 2}}
    assert MyDataClass.from_dict({"x": {"a": 2}}) == obj
