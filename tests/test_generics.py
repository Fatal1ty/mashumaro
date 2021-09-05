from dataclasses import dataclass
from datetime import datetime
from typing import Generic, List, Mapping, TypeVar

from mashumaro import DataClassDictMixin

T = TypeVar("T")
S = TypeVar("S")
P = TypeVar("P", Mapping[int, int], List[float])


def test_one_generic():
    @dataclass
    class A(Generic[T]):
        x: T

    @dataclass
    class B(A[datetime], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": "2021-08-15 00:00:00"})
    assert obj.x == datetime(2021, 8, 15)


def test_two_generics():
    @dataclass
    class A1(Generic[T]):
        x: List[T]

    @dataclass
    class A2(Generic[T, S]):
        y: Mapping[T, S]

    @dataclass
    class B(A1[int], A2[int, float], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": ["1", "2", "3"], "y": {"1": "3.14"}})
    assert obj == B(x=[1, 2, 3], y={1: 3.14})


def test_partially_concrete_generic():
    @dataclass
    class A(Generic[T, S]):
        x: Mapping[T, S]

    @dataclass
    class B(A[int, S], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1": "3.14"}})
    assert obj == B(x={1: "3.14"})


def test_partially_concrete_generic_with_bound():
    @dataclass
    class A(Generic[T, P]):
        x: Mapping[T, P]

    @dataclass
    class B(A[int, P], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1": {"1": "2", "3": "4"}}})
    assert obj == B(x={1: {1: 2, 3: 4}})
    obj = B.from_dict({"x": {"1": {"1.1": "2.2", "3.3": "4.4"}}})
    assert obj == B(x={1: [1.1, 3.3]})
    obj = B.from_dict({"x": {"1": ["1.1", "2.2", "3.3", "4.4"]}})
    assert obj == B(x={1: [1.1, 2.2, 3.3, 4.4]})


def test_concrete_generic_with_different_type_var():
    @dataclass
    class A(Generic[T]):
        x: T

    @dataclass
    class B(A[P], DataClassDictMixin):
        pass

    obj = B.from_dict({"x": {"1": "2", "3": "4"}})
    assert obj == B(x={1: 2, 3: 4})
    obj = B.from_dict({"x": {"1.1": "2.2", "3.3": "4.4"}})
    assert obj == B(x=[1.1, 3.3])
    obj = B.from_dict({"x": ["1.1", "2.2", "3.3", "4.4"]})
    assert obj == B(x=[1.1, 2.2, 3.3, 4.4])


def test_loose_generic_info_with_any_type():
    @dataclass
    class A(Generic[T]):
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
    class A(Generic[P]):
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
    class A(Generic[P]):
        x: P

    @dataclass
    class B(A):
        pass

    @dataclass
    class C(B, Generic[P]):
        y: P

    @dataclass
    class D(C[List[float]], DataClassDictMixin):
        pass

    obj = D.from_dict({"x": {"1": "2"}, "y": {"3.3": "4.4"}})
    assert obj == D(x={1: 2}, y=[3.3])
    obj = D.from_dict({"x": {"1.1": "2.2"}, "y": {"3.3": "4.4"}})
    assert obj == D(x=[1.1], y=[3.3])


def test_not_dataclass_generic():
    class MyGeneric(Generic[P, T]):
        pass

    @dataclass
    class GenericDataClass(Generic[P]):
        x: P

    @dataclass
    class DataClass(MyGeneric[P, T], GenericDataClass[P]):
        pass

    @dataclass
    class ConcreteDataClass(DataClass[List[float], float], DataClassDictMixin):
        pass

    obj = ConcreteDataClass.from_dict({"x": {"1": "2", "3": "4"}})
    assert obj == ConcreteDataClass(x=[1.0, 3.0])
