from dataclasses import dataclass
from datetime import date
from functools import partial
from typing import Generic, Tuple, TypeVar

try:
    from typing import TypeVarTuple
except ImportError:
    from typing_extensions import TypeVarTuple
try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.core.const import PY_311_MIN

# noinspection PyProtectedMember
from mashumaro.core.meta.helpers import (
    _check_generic,
    _flatten_type_args,
    resolve_type_params,
    type_name,
)
from mashumaro.core.meta.types.common import FieldContext, ValueSpec

# noinspection PyProtectedMember
from mashumaro.core.meta.types.pack import pack_tuple

# noinspection PyProtectedMember
from mashumaro.core.meta.types.unpack import unpack_tuple
from mashumaro.exceptions import MissingField

K = TypeVar("K")
V = TypeVar("V")
Ts = TypeVarTuple("Ts")


_type_name = partial(type_name, short=True)


@dataclass
class MyGenericDataClassTs(Generic[Unpack[Ts]], DataClassDictMixin):
    x: Tuple[int, Unpack[Ts]]


class MyGenericTs(Generic[Unpack[Ts]]):
    pass


class MyGenericTsK(Generic[Unpack[Ts], K]):
    pass


def test_check_generic():
    with pytest.raises(TypeError) as e:
        _check_generic(object, (K, Unpack[Ts], Unpack[Ts]), (int,))
    assert (
        str(e.value)
        == "Multiple unpacks are disallowed within a single type parameter "
        "list for object"
    )

    with pytest.raises(TypeError) as e:
        _check_generic(object, (K, V), (int,))
    assert (
        str(e.value) == f"Too few arguments for object; actual 1, expected 2"
    )

    with pytest.raises(TypeError) as e:
        _check_generic(object, (K, Unpack[Ts], V), (int,))
    assert (
        str(e.value)
        == "Too few arguments for object; actual 1, expected at least 2"
    )


def test_dataclass_with_multiple_unpacks():
    with pytest.raises(TypeError) as e:

        @dataclass
        class DataClass(DataClassDictMixin):
            x: Tuple[Unpack[Tuple[int]], Unpack[Tuple[float]]]

    typ_name = type_name(Tuple[Unpack[Tuple[int]], Unpack[Tuple[float]]])
    assert (
        str(e.value)
        == "Multiple unpacks are disallowed within a single type parameter "
        f"list for {typ_name}"
    )


def test_dataclass_with_single_unpack_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple[Unpack[Tuple[int, ...]]]
        b: Tuple[Unpack[Tuple[int, float, int]]]
        c: Tuple[Unpack[Tuple[int]]]
        d: Tuple[Unpack[Tuple[()]]]

    obj = DataClass(
        a=(1, 2, 3, 4, 5),
        b=(1, 2.2, 3),
        c=(1,),
        d=(),
    )
    assert obj.to_dict() == {
        "a": [1, 2, 3, 4, 5],
        "b": [1, 2.2, 3],
        "c": [1],
        "d": [],
    }
    assert (
        DataClass.from_dict(
            {
                "a": ["1", "2", "3", "4", 5.0],
                "b": ["1", "2.2", "3"],
                "c": ["1"],
                "d": ["1", "2", "3"],
            }
        )
        == obj
    )


def test_dataclass_with_mixed_unpack_tuple_ellipsis():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple[float, Unpack[Tuple[int, ...]]]
        b: Tuple[Unpack[Tuple[int, ...]], float]
        c: Tuple[float, Unpack[Tuple[int, ...]], float]

    obj = DataClass(
        a=(1.1, 2, 3, 4, 5),
        b=(1, 2, 3, 4, 5.5),
        c=(1.1, 2, 3, 4, 5.5),
    )
    assert obj.to_dict() == {
        "a": [1.1, 2, 3, 4, 5],
        "b": [1, 2, 3, 4, 5.5],
        "c": [1.1, 2, 3, 4, 5.5],
    }
    assert (
        DataClass.from_dict(
            {
                "a": ["1.1", "2", "3", "4", 5.0],
                "b": [1.0, "2", "3", "4", "5.5"],
                "c": ["1.1", "2", "3", 4.0, 5.5],
            }
        )
        == obj
    )


def test_dataclass_with_mixed_unpack_tuple_multiple_args():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple[float, Unpack[Tuple[int, float, int]]]
        b: Tuple[Unpack[Tuple[int, float, int]], float]
        c: Tuple[float, Unpack[Tuple[int, float, int]], float]

    obj = DataClass(
        a=(1.1, 2, 3.3, 4),
        b=(1, 2.2, 3, 4.4),
        c=(1.1, 2, 3.3, 4, 5.5),
    )
    assert obj.to_dict() == {
        "a": [1.1, 2, 3.3, 4],
        "b": [1, 2.2, 3, 4.4],
        "c": [1.1, 2, 3.3, 4, 5.5],
    }
    assert (
        DataClass.from_dict(
            {
                "a": ["1.1", "2", 3.3, 4.0],
                "b": [1.0, 2.2, "3", "4.4"],
                "c": ["1.1", "2", 3.3, 4.0, "5.5"],
            }
        )
        == obj
    )


def test_dataclass_with_mixed_unpack_tuple_one_arg():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple[float, Unpack[Tuple[int]]]
        b: Tuple[Unpack[Tuple[int]], float]
        c: Tuple[float, Unpack[Tuple[int]], float]

    obj = DataClass(
        a=(1.1, 2),
        b=(1, 2.2),
        c=(1.1, 2, 3.3),
    )
    assert obj.to_dict() == {
        "a": [1.1, 2],
        "b": [1, 2.2],
        "c": [1.1, 2, 3.3],
    }
    assert (
        DataClass.from_dict(
            {
                "a": ["1.1", 2.0],
                "b": [1.0, "2.2"],
                "c": ["1.1", 2.0, 3.3],
            }
        )
        == obj
    )


def test_dataclass_with_mixed_unpack_empty_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple[float, Unpack[Tuple[()]]]
        b: Tuple[Unpack[Tuple[()]], float]
        c: Tuple[float, Unpack[Tuple[()]], float]

    obj = DataClass(
        a=(1.1,),
        b=(1.1,),
        c=(1.1, 2.2),
    )
    assert obj.to_dict() == {
        "a": [1.1],
        "b": [1.1],
        "c": [1.1, 2.2],
    }
    assert (
        DataClass.from_dict(
            {
                "a": ["1.1"],
                "b": ["1.1"],
                "c": ["1.1", "2.2"],
            }
        )
        == obj
    )


@pytest.mark.skipif(not PY_311_MIN, reason="requires python 3.11")
def test_type_name_for_unpacks_py_311():
    assert _type_name(Tuple[Unpack[Tuple[int, ...]]]) == "Tuple[int, ...]"
    assert _type_name(Tuple[Unpack[Tuple[int, float]]]) == "Tuple[int, float]"
    assert (
        _type_name(Tuple[int, Unpack[Tuple[float, ...]]])
        == "Tuple[int, *Tuple[float, ...]]"
    )
    assert (
        _type_name(Tuple[int, Unpack[Tuple[float, str]]])
        == "Tuple[int, float, str]"
    )
    assert _type_name(Tuple[Unpack[Tuple[()]]]) == "Tuple[()]"
    assert _type_name(Tuple[int, Unpack[Tuple[()]]]) == "Tuple[int]"
    assert (
        _type_name(Tuple[str, Unpack[Tuple[int, ...]], int])
        == "Tuple[str, *Tuple[int, ...], int]"
    )
    assert (
        _type_name(Tuple[str, Unpack[Tuple[Tuple[int], ...]], int])
        == "Tuple[str, *Tuple[Tuple[int], ...], int]"
    )
    assert (
        _type_name(
            Tuple[str, Unpack[Tuple[Tuple[Unpack[Tuple[int]], ...]]], int]
        )
        == "Tuple[str, Tuple[int, ...], int]"
    )
    assert _type_name(Tuple[Unpack[Ts]]) == "Tuple[*Ts]"
    assert _type_name(Tuple[int, Unpack[Ts], int]) == "Tuple[int, *Ts, int]"
    assert _type_name(Generic[Unpack[Ts]]) == "Generic[*Ts]"
    assert _type_name(Generic[K, Unpack[Ts], V]) == "Generic[Any, *Ts, Any]"
    assert _type_name(Unpack[Tuple[int]]) == "int"
    assert _type_name(Unpack[Tuple[int, float]]) == "int, float"
    assert _type_name(Unpack[Ts]) == "*Ts"
    assert _type_name(Ts) == "Ts"
    assert (
        _type_name(Tuple[Unpack[Ts], K][Unpack[Tuple[int, ...]]])
        == "Tuple[*Tuple[int, ...], int]"
    )
    assert (
        _type_name(Tuple[Unpack[Ts], K][Unpack[Tuple[int, ...]], date])
        == "Tuple[*Tuple[int, ...], date]"
    )
    assert (
        _type_name(Tuple[Unpack[Ts], K][date, Unpack[Tuple[int, ...]]])
        == "Tuple[date, *Tuple[int, ...], int]"
    )


@pytest.mark.skipif(PY_311_MIN, reason="requires python<3.11")
def test_type_name_for_unpacks_py_less_than_311():
    assert _type_name(Tuple[Unpack[Tuple[int, ...]]]) == "Tuple[int, ...]"
    assert _type_name(Tuple[Unpack[Tuple[int, float]]]) == "Tuple[int, float]"
    assert (
        _type_name(Tuple[int, Unpack[Tuple[float, ...]]])
        == "Tuple[int, Unpack[Tuple[float, ...]]]"
    )
    assert (
        _type_name(Tuple[int, Unpack[Tuple[float, str]]])
        == "Tuple[int, float, str]"
    )
    assert _type_name(Tuple[Unpack[Tuple[()]]]) == "Tuple[()]"
    assert _type_name(Tuple[int, Unpack[Tuple[()]]]) == "Tuple[int]"
    assert (
        _type_name(Tuple[str, Unpack[Tuple[int, ...]], int])
        == "Tuple[str, Unpack[Tuple[int, ...]], int]"
    )
    assert (
        _type_name(Tuple[str, Unpack[Tuple[Tuple[int], ...]], int])
        == "Tuple[str, Unpack[Tuple[Tuple[int], ...]], int]"
    )
    assert (
        _type_name(
            Tuple[str, Unpack[Tuple[Tuple[Unpack[Tuple[int]], ...]]], int]
        )
        == "Tuple[str, Tuple[int, ...], int]"
    )
    assert _type_name(Tuple[Unpack[Ts]]) == "Tuple[Unpack[Ts]]"
    assert (
        _type_name(Tuple[int, Unpack[Ts], int])
        == "Tuple[int, Unpack[Ts], int]"
    )
    assert _type_name(Generic[Unpack[Ts]]) == "Generic[Unpack[Ts]]"
    assert (
        _type_name(Generic[K, Unpack[Ts], V])
        == "Generic[Any, Unpack[Ts], Any]"
    )
    assert _type_name(Unpack[Tuple[int]]) == "int"
    assert _type_name(Unpack[Tuple[int, float]]) == "int, float"
    assert _type_name(Unpack[Ts]) == "Unpack[Ts]"
    assert _type_name(Ts) == "Ts"

    # this doesn't work on python<3.11
    # assert (
    #     _type_name(Tuple[Unpack[Ts], K][Unpack[Tuple[int, ...]]])
    #     == "Tuple[Unpack[Tuple[int, ...]], int]"
    # )
    # assert (
    #     _type_name(Tuple[Unpack[Ts], K][Unpack[Tuple[int, ...]], date])
    #     == "Tuple[Unpack[Tuple[int, ...]], date]"
    # )
    # assert (
    #     _type_name(Tuple[Unpack[Ts], K][date, Unpack[Tuple[int, ...]]])
    #     == "Tuple[date, Unpack[Tuple[int, ...]], int]"
    # )


def test_concrete_generic_with_empty_tuple():
    @dataclass
    # I tried MyGenericDataClassTs[()] but [()] becomes just (). Impossible.
    class ConcreteDataClass(MyGenericDataClassTs[Unpack[Tuple[()]]]):
        pass

    obj = ConcreteDataClass((1,))
    assert obj.to_dict() == {"x": [1]}
    assert ConcreteDataClass.from_dict({"x": [1]}) == obj
    assert ConcreteDataClass.from_dict({"x": [1, 2, 3]}) == obj


def test_concrete_generic_with_variable_length_tuple_any():
    @dataclass
    class ConcreteDataClass(MyGenericDataClassTs):
        pass

    obj = ConcreteDataClass((1, "a", date(2022, 12, 17)))
    assert obj.to_dict() == {"x": [1, "a", date(2022, 12, 17)]}
    assert (
        ConcreteDataClass.from_dict({"x": ["1", "a", date(2022, 12, 17)]})
        == obj
    )


def test_concrete_generic_with_replaced_tuple_with_one_arg():
    @dataclass
    class ConcreteDataClass(MyGenericDataClassTs[Unpack[Tuple[K]]]):
        pass

    obj = ConcreteDataClass((1, date(2022, 12, 17)))
    assert obj.to_dict() == {"x": [1, date(2022, 12, 17)]}
    assert (
        ConcreteDataClass.from_dict({"x": ["1", date(2022, 12, 17), "a"]})
        == obj
    )


def test_concrete_generic_with_replaced_tuple_with_multiple_args():
    @dataclass
    class ConcreteDataClass(MyGenericDataClassTs[Unpack[Tuple[float, float]]]):
        pass

    obj = ConcreteDataClass((1, 2.2, 3.3))
    assert obj.to_dict() == {"x": [1, 2.2, 3.3]}
    assert ConcreteDataClass.from_dict({"x": ["1", "2.2", "3.3"]}) == obj


@pytest.mark.skipif(not PY_311_MIN, reason="doesn't work on py<3.11")
def test_with_int_float_tuple_and_any_at_the_end():
    Ts1 = TypeVarTuple("Ts1")
    Ts2 = TypeVarTuple("Ts2")
    IntTuple = Tuple[int, Unpack[Ts1]]
    IntFloatTuple = IntTuple[float, Unpack[Ts2]]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: IntFloatTuple

    obj = DataClass((1, 2.2, "3", date(2022, 12, 17)))
    assert obj.to_dict() == {"x": [1, 2.2, "3", date(2022, 12, 17)]}
    assert (
        DataClass.from_dict({"x": ["1", "2.2", "3", date(2022, 12, 17)]})
        == obj
    )


@pytest.mark.skipif(not PY_311_MIN, reason="doesn't work on py<3.11")
def test_with_int_floats_tuple():
    Ts1 = TypeVarTuple("Ts1")
    IntTuple = Tuple[int, Unpack[Ts1]]
    IntFloatsTuple = IntTuple[Unpack[Tuple[float, ...]]]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: IntFloatsTuple

    obj = DataClass((1, 2.2, 3.3, 4.4))
    assert obj.to_dict() == {"x": [1, 2.2, 3.3, 4.4]}
    assert DataClass.from_dict({"x": ["1", "2.2", "3.3", "4.4"]}) == obj


@pytest.mark.skipif(not PY_311_MIN, reason="doesn't work on py<3.11")
def test_splitting_arbitrary_length_tuples_1():
    Elderberries = Tuple[Unpack[Ts], K]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Elderberries[Unpack[Tuple[int, ...]]]

    obj = DataClass((1, 2, 3))
    assert obj.to_dict() == {"x": [1, 2, 3]}
    assert DataClass.from_dict({"x": ["1", "2", "3"]}) == obj

    obj = DataClass((1,))
    assert obj.to_dict() == {"x": [1]}
    assert DataClass.from_dict({"x": [1]}) == obj


def test_dataclass_with_splitting_arbitrary_length_tuples_1():
    @dataclass
    class GenericDataClass(Generic[Unpack[Ts], K], DataClassDictMixin):
        x: Tuple[Unpack[Ts], K]

    @dataclass
    class ConcreteDataClass(GenericDataClass[Unpack[Tuple[int, ...]]]):
        pass

    obj = ConcreteDataClass((1, 2, 3))
    assert obj.to_dict() == {"x": [1, 2, 3]}
    assert ConcreteDataClass.from_dict({"x": ["1", "2", "3"]}) == obj

    obj = ConcreteDataClass((1,))
    assert obj.to_dict() == {"x": [1]}
    assert ConcreteDataClass.from_dict({"x": [1]}) == obj


@pytest.mark.skipif(not PY_311_MIN, reason="doesn't work on py<3.11")
def test_splitting_arbitrary_length_tuples_2():
    Elderberries = Tuple[Unpack[Ts], K]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Elderberries[Unpack[Tuple[int, ...]], date]

    obj = DataClass((1, 2, date(2022, 12, 17)))
    assert obj.to_dict() == {"x": [1, 2, "2022-12-17"]}
    assert DataClass.from_dict({"x": ["1", "2", "2022-12-17"]}) == obj

    obj = DataClass((date(2022, 12, 17),))
    assert obj.to_dict() == {"x": ["2022-12-17"]}
    assert DataClass.from_dict({"x": ["2022-12-17"]}) == obj


def test_dataclass_with_splitting_arbitrary_length_tuples_2():
    @dataclass
    class GenericDataClass(Generic[Unpack[Ts], K], DataClassDictMixin):
        x: Tuple[Unpack[Ts], K]

    @dataclass
    class ConcreteDataClass(GenericDataClass[Unpack[Tuple[int, ...]], date]):
        pass

    obj = ConcreteDataClass((1, 2, date(2022, 12, 17)))
    assert obj.to_dict() == {"x": [1, 2, "2022-12-17"]}
    assert ConcreteDataClass.from_dict({"x": ["1", "2", "2022-12-17"]}) == obj

    obj = ConcreteDataClass((date(2022, 12, 17),))
    assert obj.to_dict() == {"x": ["2022-12-17"]}
    assert ConcreteDataClass.from_dict({"x": ["2022-12-17"]}) == obj


@pytest.mark.skipif(not PY_311_MIN, reason="doesn't work on py<3.11")
def test_splitting_arbitrary_length_tuples_3():
    Elderberries = Tuple[Unpack[Ts], K]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Elderberries[date, Unpack[Tuple[int, ...]]]

    obj = DataClass((date(2022, 12, 17), 1, 2, 3))
    assert obj.to_dict() == {"x": ["2022-12-17", 1, 2, 3]}
    assert DataClass.from_dict({"x": ["2022-12-17", "1", "2", "3"]}) == obj

    obj = DataClass((date(2022, 12, 17), 1))
    assert obj.to_dict() == {"x": ["2022-12-17", 1]}
    assert DataClass.from_dict({"x": ["2022-12-17", "1"]}) == obj


def test_dataclass_with_splitting_arbitrary_length_tuples_3():
    @dataclass
    class GenericDataClass(Generic[Unpack[Ts], K], DataClassDictMixin):
        x: Tuple[Unpack[Ts], K]

    @dataclass
    class ConcreteDataClass(GenericDataClass[date, Unpack[Tuple[int, ...]]]):
        pass

        class Config:
            debug = True

    obj = ConcreteDataClass((date(2022, 12, 17), 1, 2))
    assert obj.to_dict() == {"x": ["2022-12-17", 1, 2]}
    assert ConcreteDataClass.from_dict({"x": ["2022-12-17", "1", "2"]}) == obj

    obj = ConcreteDataClass((date(2022, 12, 17), 1))
    assert obj.to_dict() == {"x": ["2022-12-17", 1]}
    assert ConcreteDataClass.from_dict({"x": ["2022-12-17", 1]}) == obj


def test_resolve_type_params_with_unpacks():
    assert resolve_type_params(MyGenericTsK, [int, float], False) == {
        MyGenericTsK: {K: float, Unpack[Ts]: Unpack[Tuple[int]]}
    }
    assert resolve_type_params(MyGenericTsK, [int, str, float], False) == {
        MyGenericTsK: {K: float, Unpack[Ts]: Unpack[Tuple[int, str]]}
    }
    assert resolve_type_params(
        MyGenericTsK, [Unpack[Tuple[int, str]], float], False
    ) == {MyGenericTsK: {K: float, Unpack[Ts]: Unpack[Tuple[int, str]]}}
    assert resolve_type_params(
        MyGenericTsK, [Unpack[Tuple[int, ...]]], False
    ) == {MyGenericTsK: {K: int, Unpack[Ts]: Unpack[Tuple[int, ...]]}}
    assert resolve_type_params(
        MyGenericTsK, [str, Unpack[Tuple[int, ...]]], False
    ) == {
        MyGenericTsK: {
            K: int,
            Unpack[Ts]: Unpack[Tuple[str, Unpack[Tuple[int, ...]]]],
        }
    }
    assert resolve_type_params(MyGenericTs, [()], False) == {
        MyGenericTs: {Unpack[Ts]: Unpack[Tuple[()]]}
    }


def test_dataclass_with_tuple_int_and_empty():
    @dataclass
    class ConcreteDataClass(MyGenericDataClassTs[Unpack[Tuple[()]]]):
        pass

    obj = ConcreteDataClass((1,))
    assert obj.to_dict() == {"x": [1]}
    assert ConcreteDataClass.from_dict({"x": [1]}) == obj
    assert ConcreteDataClass.from_dict({"x": [1, 2, 3]}) == obj
    with pytest.raises(MissingField):
        ConcreteDataClass.from_dict({})


def test_unpack_tuple_with_multiple_unpacks():
    spec = ValueSpec(
        type=Tuple,
        expression="value",
        builder=object,
        field_ctx=FieldContext("x", {}),
    )
    with pytest.raises(TypeError):
        unpack_tuple(spec, (Unpack[Tuple[int]], Unpack[Tuple[float]]))
    with pytest.raises(TypeError):
        pack_tuple(spec, (Unpack[Tuple[int]], Unpack[Tuple[float]]))


def test_flatten_type_args_with_empty_tuple():
    assert _flatten_type_args([Unpack[Tuple[()]]]) == [()]
    assert _flatten_type_args([int, Unpack[Tuple[()]]]) == [int]
    assert _flatten_type_args([Unpack[tuple[()]]]) == [()]
    assert _flatten_type_args([int, Unpack[tuple[()]]]) == [int]
