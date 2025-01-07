from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Mapping

from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import SerializableType
from tests.entities import MyGenericDataClass, SerializableTypeGenericList


@dataclass
class Foo[T](DataClassJSONMixin):
    x: T
    y: "Foo[Any] | None"


@dataclass
class Bar(Foo):
    pass


@dataclass
class GenericSerializableType[T](SerializableType):
    value: object

    def _serialize(self):
        return self.value

    @classmethod
    def _deserialize(cls, value):
        return cls(value)


def test_one_generic():
    @dataclass
    class A[T]:
        x: T

    @dataclass
    class B(A[datetime], DataClassDictMixin):
        pass

    obj = B(datetime(2021, 8, 15))
    assert B.from_dict({"x": "2021-08-15T00:00:00"}) == obj
    assert obj.to_dict() == {"x": "2021-08-15T00:00:00"}


def test_one_generic_list():
    @dataclass
    class A[T](list[T]):
        x: list[T]

    @dataclass
    class B(A[datetime], DataClassDictMixin):
        pass

    obj = B(x=[datetime(2021, 8, 15)])
    assert B.from_dict({"x": ["2021-08-15T00:00:00"]}) == obj
    assert obj.to_dict() == {"x": ["2021-08-15T00:00:00"]}


def test_two_generics():
    @dataclass
    class A1[T]:
        x: list[T]

    @dataclass
    class A2[T, S]:
        y: Mapping[T, S]

    @dataclass
    class B(A1[datetime], A2[datetime, date], DataClassDictMixin):
        pass

    obj = B(
        x=[datetime(2021, 8, 15), datetime(2021, 8, 16)],
        y={datetime(2021, 8, 17): date(2021, 8, 18)},
    )
    dump = {
        "x": ["2021-08-15T00:00:00", "2021-08-16T00:00:00"],
        "y": {"2021-08-17T00:00:00": "2021-08-18"},
    }
    assert B.from_dict(dump) == obj
    assert obj.to_dict() == dump


def test_partially_concrete_generic():
    @dataclass
    class A[T, S]:
        x: Mapping[T, S]

    @dataclass
    class B[S](A[datetime, S], DataClassDictMixin):
        pass

    obj = B(x={datetime(2022, 11, 21): "3.14"})
    assert B.from_dict({"x": {"2022-11-21T00:00:00": "3.14"}}) == obj
    assert obj.to_dict() == {"x": {"2022-11-21T00:00:00": "3.14"}}


def test_partially_concrete_generic_with_bound():
    @dataclass
    class A[T, P: (Mapping[int, int], list[float])]:
        x: Mapping[T, P]

    @dataclass
    class B[P: (Mapping[int, int], list[float])](
        A[date, P], DataClassDictMixin
    ):
        pass

    obj1 = B(x={date(2022, 11, 21): {1: 2, 3: 4}})
    assert B.from_dict({"x": {"2022-11-21": {"1": "2", "3": "4"}}}) == obj1
    assert obj1.to_dict() == {"x": {"2022-11-21": {1: 2, 3: 4}}}
    obj2 = B(x={date(2022, 11, 21): [1.1, 3.3]})
    assert (
        B.from_dict({"x": {"2022-11-21": {"1.1": "2.2", "3.3": "4.4"}}})
        == obj2
    )
    assert obj2.to_dict() == {"x": {"2022-11-21": [1.1, 3.3]}}
    obj3 = B(x={date(2022, 11, 21): [1.1, 2.2, 3.3, 4.4]})
    assert (
        B.from_dict({"x": {"2022-11-21": ["1.1", "2.2", "3.3", "4.4"]}})
        == obj3
    )
    assert obj3.to_dict() == {"x": {"2022-11-21": [1.1, 2.2, 3.3, 4.4]}}


def test_concrete_generic_with_different_type_var():
    @dataclass
    class A[T]:
        x: T

    @dataclass
    class B[P: (Mapping[int, int], list[float])](A[P], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1": "2", "3": "4"}})
    assert obj == B(x={1: 2, 3: 4})
    obj = B.from_dict({"x": {"1.1": "2.2", "3.3": "4.4"}})
    assert obj == B(x=[1.1, 3.3])
    obj = B.from_dict({"x": ["1.1", "2.2", "3.3", "4.4"]})
    assert obj == B(x=[1.1, 2.2, 3.3, 4.4])


def test_loose_generic_info_with_any_type():
    @dataclass
    class A[T]:
        x: T

    @dataclass
    class B(A, DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1.1": "2.2", "3.3": "4.4"}})
    assert obj == B(x={"1.1": "2.2", "3.3": "4.4"})
    obj = B.from_dict({"x": ["1.1", "2.2", "3.3", "4.4"]})
    assert obj == B(x=["1.1", "2.2", "3.3", "4.4"])


def test_loose_generic_info_with_bound():
    @dataclass
    class A[P: (Mapping[int, int], list[float])]:
        x: P

    @dataclass
    class B(A, DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1": "2", "3": "4"}})
    assert obj == B(x={1: 2, 3: 4})
    obj = B.from_dict({"x": {"1.1": "2.2", "3.3": "4.4"}})
    assert obj == B(x=[1.1, 3.3])
    obj = B.from_dict({"x": ["1.1", "2.2", "3.3", "4.4"]})
    assert obj == B(x=[1.1, 2.2, 3.3, 4.4])


def test_loose_generic_info_in_first_generic():
    @dataclass
    class A[P: (Mapping[int, int], list[float])]:
        x: P

    @dataclass
    class B(A):
        pass

    @dataclass
    class C[P: (Mapping[int, int], list[float])](B):
        y: P

    @dataclass
    class D(C[list[float]], DataClassDictMixin):
        pass

    obj = D.from_dict({"x": {"1": "2"}, "y": {"3.3": "4.4"}})
    assert obj == D(x={1: 2}, y=[3.3])
    obj = D.from_dict({"x": {"1.1": "2.2"}, "y": {"3.3": "4.4"}})
    assert obj == D(x=[1.1], y=[3.3])


def test_not_dataclass_generic():
    class MyGeneric[P: (Mapping[int, int], list[float]), T]:
        pass

    @dataclass
    class GenericDataClass[P: (Mapping[int, int], list[float])]:
        x: P

    @dataclass
    class DataClass[P: (Mapping[int, int], list[float]), T](
        MyGeneric[P, T], GenericDataClass[P]
    ):
        pass

    @dataclass
    class ConcreteDataClass(DataClass[list[float], float], DataClassDictMixin):
        pass

    obj = ConcreteDataClass.from_dict({"x": {"1": "2", "3": "4"}})
    assert obj == ConcreteDataClass(x=[1.0, 3.0])


def test_generic_dataclass_as_field_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        date: MyGenericDataClass[date]
        str: MyGenericDataClass[str]

    obj = DataClass(
        date=MyGenericDataClass(date(2021, 9, 14)),
        str=MyGenericDataClass("2021-09-14"),
    )
    dictionary = {"date": {"x": "2021-09-14"}, "str": {"x": "2021-09-14"}}
    assert DataClass.from_dict(dictionary) == obj
    assert obj.to_dict() == dictionary


def test_serializable_type_generic_class():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: SerializableTypeGenericList[str]

    obj = DataClass(SerializableTypeGenericList(["a", "b", "c"]))
    assert DataClass.from_dict({"x": ["a", "b", "c"]}) == obj
    assert obj.to_dict() == {"x": ["a", "b", "c"]}


def test_self_referenced_generic_no_max_recursion_error():
    obj = Bar(42, Foo(33, None))
    assert obj.to_dict() == {"x": 42, "y": {"x": 33, "y": None}}
    assert Bar.from_dict({"x": 42, "y": {"x": 33, "y": None}}) == obj
    assert obj.to_json() == '{"x": 42, "y": {"x": 33, "y": null}}'
    assert Bar.from_json('{"x": 42, "y": {"x": 33, "y": null}}') == obj


# Regression test for https://github.com/Fatal1ty/mashumaro/issues/274.
def test_generic_serializable_type_getitem():
    @dataclass
    class DataClass(DataClassDictMixin):
        # Simply specializing the type would lead to an AttributeError.
        x: GenericSerializableType[int]
