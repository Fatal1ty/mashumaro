from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

import ciso8601
import pytest

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import (
    UnserializableField,
    UnsupportedDeserializationEngine,
    UnsupportedSerializationEngine,
)
from mashumaro.types import SerializationStrategy

from .entities import (
    MutableString,
    MyList,
    MyNamedTuple,
    MyNamedTupleWithDefaults,
    MyUntypedNamedTuple,
    MyUntypedNamedTupleWithDefaults,
    ThirdPartyType,
    TIntStr,
    TypedDictRequiredKeys,
)


def test_ciso8601_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_ciso8601_date_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: date = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=date(2021, 1, 2))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_ciso8601_time_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: time = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=time(3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_pendulum_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=datetime(2008, 12, 29, 7, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2009-W01 07:00"})
    assert instance == should_be


def test_pendulum_date_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: date = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=date(2008, 12, 29))
    instance = DataClass.from_dict({"x": "2009-W01"})
    assert instance == should_be


def test_pendulum_time_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: time = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=time(3, 4, 5))
    instance = DataClass.from_dict({"x": "2009-W01 03:04:05"})
    assert instance == should_be


def test_unsupported_datetime_parser_engine():
    with pytest.raises(UnsupportedDeserializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: datetime = field(metadata={"deserialize": "unsupported"})


def test_global_function_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"deserialize": ciso8601.parse_datetime_as_naive}
        )

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05+03:00"})
    assert instance == should_be


def test_local_function_datetime_parser():
    def parse_dt(s):
        return ciso8601.parse_datetime_as_naive(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": parse_dt})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05+03:00"})
    assert instance == should_be


def test_class_method_datetime_parser():
    class DateTimeParser:
        @classmethod
        def parse_dt(cls, s: str) -> datetime:
            return datetime.fromisoformat(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": DateTimeParser.parse_dt})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05"})
    assert instance == should_be


def test_class_instance_method_datetime_parser():
    class DateTimeParser:
        def __call__(self, s: str) -> datetime:
            return datetime.fromisoformat(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": DateTimeParser()})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05"})
    assert instance == should_be


def test_callable_class_instance_datetime_parser():
    class CallableDateTimeParser:
        def __call__(self, s):
            return ciso8601.parse_datetime(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": CallableDateTimeParser()})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_lambda_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"deserialize": lambda s: ciso8601.parse_datetime(s)}
        )

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_derived_dataclass_metadata_deserialize_option():
    @dataclass
    class A:
        x: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})

    @dataclass
    class B(A, DataClassDictMixin):
        y: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})

    should_be = B(
        x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        y=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )
    instance = B.from_dict(
        {"x": "2021-01-02T03:04:05Z", "y": "2021-01-02T03:04:05Z"}
    )
    assert instance == should_be


def test_derived_dataclass_metadata_deserialize_option_removed():
    class MyClass:
        pass

    @dataclass
    class A:
        x: MyClass = field(
            metadata={"deserialize": MyClass, "serialize": lambda obj: obj.i}
        )

    with pytest.raises(UnserializableField):

        @dataclass
        class _(A, DataClassDictMixin):
            x: MyClass


def test_bytearray_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: bytearray = field(
            metadata={"deserialize": lambda s: s.upper().encode()}
        )

    should_be = DataClass(x=bytearray(b"ABC"))
    instance = DataClass.from_dict({"x": "abc"})
    assert instance == should_be


def test_path_like_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Path = field(
            metadata={"deserialize": lambda s: Path(str(s).upper())}
        )

    should_be = DataClass(x=Path("/ABC"))
    instance = DataClass.from_dict({"x": "/abc"})
    assert instance == should_be


def test_datetime_serialize_option():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"serialize": lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        )

    should_be = {"x": "2021-01-02 03:04:05"}
    instance = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    assert instance.to_dict() == should_be


def test_third_party_type_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: ThirdPartyType = field(
            metadata={
                "deserialize": lambda v: ThirdPartyType(v),
                "serialize": lambda v: v.value,
            }
        )

    should_be = DataClass(x=ThirdPartyType(123))
    instance = DataClass.from_dict({"x": 123})
    assert instance == should_be
    assert instance.to_dict() == {"x": 123}


def test_serializable_type_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MutableString = field(
            metadata={
                "deserialize": lambda s: MutableString(s.upper()),
                "serialize": lambda v: str(v).lower(),
            }
        )

    should_be = DataClass(x=MutableString("ABC"))
    instance = DataClass.from_dict({"x": "abc"})
    assert instance == should_be
    assert instance.to_dict() == {"x": "abc"}


def test_optional_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[ThirdPartyType] = field(
            metadata={
                "deserialize": lambda v: ThirdPartyType(v),
                "serialize": lambda v: v.value,
            }
        )

    instance = DataClass.from_dict({"x": 123})
    assert instance
    assert instance.x.value == 123
    dct = instance.to_dict()
    assert dct["x"] == 123


def test_union_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Union[float, int] = field(
            metadata={
                "deserialize": lambda v: int(v),
                "serialize": lambda v: int(v),
            }
        )

    instance = DataClass.from_dict({"x": 1.0})
    assert instance == DataClass(x=1)
    assert instance.to_dict() == {"x": 1}
    for attr in dir(DataClass):
        assert not attr.startswith("__unpack_union")
        assert not attr.startswith("__unpack_union")


def test_type_var_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TIntStr = field(
            metadata={
                "deserialize": lambda v: v * 2,
                "serialize": lambda v: v * 2,
            }
        )

    instance = DataClass.from_dict({"x": "a"})
    assert instance == DataClass(x="aa")
    assert instance.to_dict() == {"x": "aaaa"}
    for attr in dir(DataClass):
        assert not attr.startswith("__unpack_type_var")
        assert not attr.startswith("__pack_type_var")


def test_serialization_strategy():
    class TestSerializationStrategy(SerializationStrategy):
        def serialize(self, value):
            return [value]

        def deserialize(self, value):
            return value[0]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(
            metadata={"serialization_strategy": TestSerializationStrategy()}
        )

    instance = DataClass(x=123)
    assert DataClass.from_dict({"x": [123]}) == instance
    assert instance.to_dict() == {"x": [123]}


def test_collection_derived_custom_class():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyList = field(
            metadata={"serialize": lambda v: v, "deserialize": lambda v: v}
        )

    instance = DataClass(x=[1, 2, 3])
    assert DataClass.from_dict({"x": [1, 2, 3]}) == instance
    assert instance.to_dict() == {"x": [1, 2, 3]}


def test_dataclass_with_typed_dict_overridden():
    def serialize_x(x: TypedDictRequiredKeys) -> Dict[str, Any]:
        return {"int": int(x["int"]), "float": float(x["float"])}

    def deserialize_x(x: Dict[str, Any]) -> TypedDictRequiredKeys:
        return TypedDictRequiredKeys(int=x["int"], float=x["float"])

    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictRequiredKeys = field(
            metadata={"serialize": serialize_x, "deserialize": deserialize_x}
        )

    obj = DataClass(x=TypedDictRequiredKeys(int=1, float=2.0))
    data = {"x": {"int": 1, "float": 2.0}}
    assert DataClass.from_dict(data) == obj
    assert obj.to_dict() == data


def test_named_tuple_as_dict_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyNamedTuple = field(
            metadata={"serialize": "as_dict", "deserialize": "as_dict"}
        )

    obj = DataClass(x=MyNamedTuple(i=1, f=2.0))
    assert obj.to_dict() == {"x": {"i": 1, "f": 2.0}}
    assert DataClass.from_dict({"x": {"i": 1, "f": 2.0}}) == obj


def test_named_tuple_with_defaults_as_dict_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyNamedTupleWithDefaults = field(
            metadata={"serialize": "as_dict", "deserialize": "as_dict"}
        )

    obj = DataClass(x=MyNamedTupleWithDefaults(i=1, f=2.0))
    assert obj.to_dict() == {"x": {"i": 1, "f": 2.0}}
    assert DataClass.from_dict({"x": {"i": 1, "f": 2.0}}) == obj


def test_untyped_named_tuple_as_dict_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyUntypedNamedTuple = field(
            metadata={"serialize": "as_dict", "deserialize": "as_dict"}
        )

    obj = DataClass(x=MyUntypedNamedTuple(i=1, f=2.0))
    assert obj.to_dict() == {"x": {"i": 1, "f": 2.0}}
    assert DataClass.from_dict({"x": {"i": 1, "f": 2.0}}) == obj


def test_untyped_named_tuple_with_defaults_as_dict_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyUntypedNamedTupleWithDefaults = field(
            metadata={"serialize": "as_dict", "deserialize": "as_dict"}
        )

    obj = DataClass(x=MyUntypedNamedTupleWithDefaults(i=1, f=2.0))
    assert obj.to_dict() == {"x": {"i": 1, "f": 2.0}}
    assert DataClass.from_dict({"x": {"i": 1, "f": 2.0}}) == obj


def test_unsupported_named_tuple_deserialization_engine():
    with pytest.raises(UnsupportedDeserializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyNamedTuple = field(metadata={"deserialize": "unsupported"})

    with pytest.raises(UnsupportedDeserializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyNamedTupleWithDefaults = field(
                metadata={"deserialize": "unsupported"}
            )

    with pytest.raises(UnsupportedDeserializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyUntypedNamedTuple = field(
                metadata={"deserialize": "unsupported"}
            )

    with pytest.raises(UnsupportedDeserializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyUntypedNamedTupleWithDefaults = field(
                metadata={"deserialize": "unsupported"}
            )


def test_unsupported_named_tuple_serialization_engine():
    with pytest.raises(UnsupportedSerializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyNamedTuple = field(metadata={"serialize": "unsupported"})

    with pytest.raises(UnsupportedSerializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyNamedTupleWithDefaults = field(
                metadata={"serialize": "unsupported"}
            )

    with pytest.raises(UnsupportedSerializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyUntypedNamedTuple = field(
                metadata={"serialize": "unsupported"}
            )

    with pytest.raises(UnsupportedSerializationEngine):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: MyUntypedNamedTupleWithDefaults = field(
                metadata={"serialize": "unsupported"}
            )


def test_field_metadata_omit_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(metadata={"serialize": "omit"})

    obj = DataClass(x=42)
    assert obj.to_dict() == {}
    assert DataClass.from_dict({"x": 42}) == obj
