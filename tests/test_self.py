from dataclasses import dataclass
from typing import Optional

import orjson
from typing_extensions import Self

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.codecs.orjson import ORJSONDecoder, ORJSONEncoder
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class DataClassDict(DataClassDictMixin):
    next: Optional[Self] = None


@dataclass
class DataClassDictChild(DataClassDict):
    x: int = 42


@dataclass
class DataClassDictWithoutMixin:
    next: Optional[Self] = None


@dataclass
class DataClassOrjson(DataClassORJSONMixin):
    next: Optional[Self] = None


@dataclass
class DataClassOrjsonChild(DataClassOrjson):
    x: int = 42


def test_dataclass_dict_with_self():
    obj = DataClassDict(DataClassDict())
    assert obj.to_dict() == {"next": {"next": None}}
    assert DataClassDict.from_dict({"next": {"next": None}}) == obj
    assert DataClassDict().to_dict() == {"next": None}
    assert DataClassDict.from_dict({"next": None}) == DataClassDict()
    assert DataClassDict.from_dict({}) == DataClassDict()


def test_dataclass_dict_with_self_without_mixin():
    decoder = BasicDecoder(DataClassDictWithoutMixin)
    encoder = BasicEncoder(DataClassDictWithoutMixin)
    obj = DataClassDictWithoutMixin(DataClassDictWithoutMixin())
    assert encoder.encode(obj) == {"next": {"next": None}}
    assert decoder.decode({"next": {"next": None}}) == obj
    assert encoder.encode(DataClassDictWithoutMixin()) == {"next": None}
    assert decoder.decode({"next": None}) == DataClassDictWithoutMixin()
    assert decoder.decode({}) == DataClassDictWithoutMixin()


def test_dataclass_dict_child_with_self():
    obj = DataClassDictChild(DataClassDictChild())
    assert obj.to_dict() == {"x": 42, "next": {"x": 42, "next": None}}
    assert DataClassDictChild.from_dict({"next": {"next": None}}) == obj
    assert DataClassDictChild().to_dict() == {"x": 42, "next": None}
    assert DataClassDictChild.from_dict({"next": None}) == DataClassDictChild()
    assert DataClassDictChild.from_dict({}) == DataClassDictChild()


def test_dataclass_orjson_with_self():
    obj = DataClassOrjson(DataClassOrjson())
    assert obj.to_dict() == {"next": {"next": None}}
    assert DataClassOrjson.from_dict({"next": {"next": None}}) == obj
    assert DataClassOrjson().to_dict() == {"next": None}
    assert DataClassOrjson.from_dict({"next": None}) == DataClassOrjson()
    assert DataClassOrjson.from_dict({}) == DataClassOrjson()

    dump = orjson.dumps({"next": {"next": None}})
    assert obj.to_jsonb() == dump
    assert DataClassOrjson.from_json(dump) == obj
    dump = orjson.dumps({"next": None})
    assert DataClassOrjson().to_jsonb() == dump
    assert DataClassOrjson.from_json(dump) == DataClassOrjson()
    assert DataClassOrjson.from_json(b"{}") == DataClassOrjson()


def test_dataclass_orjson_with_self_without_mixin():
    decoder = ORJSONDecoder(DataClassDictWithoutMixin)
    encoder = ORJSONEncoder(DataClassDictWithoutMixin)
    obj = DataClassDictWithoutMixin(DataClassDictWithoutMixin())
    dump = orjson.dumps({"next": {"next": None}})
    assert encoder.encode(obj) == dump
    assert decoder.decode(dump) == obj
    dump = orjson.dumps({"next": None})
    assert encoder.encode(DataClassDictWithoutMixin()) == dump
    assert decoder.decode(dump) == DataClassDictWithoutMixin()
    assert decoder.decode(b"{}") == DataClassDictWithoutMixin()


def test_dataclass_orjson_child_with_self():
    obj = DataClassOrjsonChild(DataClassOrjsonChild())
    assert obj.to_dict() == {"x": 42, "next": {"x": 42, "next": None}}
    assert DataClassOrjsonChild.from_dict({"next": {"next": None}}) == obj
    assert DataClassOrjsonChild().to_dict() == {"x": 42, "next": None}
    assert (
        DataClassOrjsonChild.from_dict({"next": None})
        == DataClassOrjsonChild()
    )
    assert DataClassOrjsonChild.from_dict({}) == DataClassOrjsonChild()

    dump = orjson.dumps({"next": {"next": None, "x": 42}, "x": 42})
    assert obj.to_jsonb() == dump
    assert DataClassOrjsonChild.from_json(dump) == obj
    dump = orjson.dumps({"next": None, "x": 42})
    assert DataClassOrjsonChild().to_jsonb() == dump
    assert DataClassOrjsonChild.from_json(dump) == DataClassOrjsonChild()
    assert DataClassOrjsonChild.from_json(b"{}") == DataClassOrjsonChild()
