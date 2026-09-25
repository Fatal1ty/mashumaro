import sys
import types
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Generic, TypeVar

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.core.meta.helpers import get_slice_type_args


@pytest.mark.parametrize(
    ("value", "dumped"),
    (
        (slice(0, 5, 2), [0, 5, 2]),
        (slice(1, 10, 3), [1, 10, 3]),
        (slice(5), [None, 5, None]),
        (slice(1, 10), [1, 10, None]),
        (slice(None, None, None), [None, None, None]),
        (slice(None, 5, None), [None, 5, None]),
        (slice(-10, -1, -1), [-10, -1, -1]),
        (slice(0, None, 2), [0, None, 2]),
    ),
)
def test_slice_to_dict_from_dict(value, dumped):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: slice

    instance = DataClass(value)
    assert instance.to_dict() == {"x": dumped}
    assert DataClass.from_dict({"x": dumped}) == instance
    assert DataClass.from_dict(instance.to_dict()) == instance


def test_optional_slice():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: slice | None

    assert DataClass(None).to_dict() == {"x": None}
    assert DataClass.from_dict({"x": None}) == DataClass(None)
    assert DataClass(slice(1, 2, 3)).to_dict() == {"x": [1, 2, 3]}
    assert DataClass.from_dict({"x": [1, 2, 3]}) == DataClass(slice(1, 2, 3))


def test_list_of_slices():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: list[slice]

    instance = DataClass([slice(0, 5), slice(1, 10, 2)])
    dumped = {"x": [[0, 5, None], [1, 10, 2]]}
    assert instance.to_dict() == dumped
    assert DataClass.from_dict(dumped) == instance


@pytest.mark.parametrize(
    ("slice_type", "expected"),
    (
        (slice, (Any, Any, Any)),
        (types.GenericAlias(slice, (date,)), (date, date, date)),
        (
            types.GenericAlias(slice, (date, timedelta)),
            (date, timedelta, date | timedelta),
        ),
        (
            types.GenericAlias(slice, (date, date, timedelta)),
            (date, date, timedelta),
        ),
    ),
)
def test_get_slice_type_args(slice_type, expected):
    assert get_slice_type_args(slice_type) == expected


def test_too_many_slice_type_args():
    slice_type = types.GenericAlias(slice, (int, int, int, int))
    with pytest.raises(
        TypeError, match="slice accepts at most 3 type arguments, got 4"
    ):
        get_slice_type_args(slice_type)


@pytest.mark.parametrize(
    ("slice_type", "value", "dumped"),
    (
        (
            types.GenericAlias(slice, (date,)),
            slice(date(2026, 1, 1), None, date(2026, 1, 3)),
            ["2026-01-01", None, "2026-01-03"],
        ),
        (
            types.GenericAlias(slice, (date, timedelta)),
            slice(date(2026, 1, 1), timedelta(days=2), date(2026, 1, 3)),
            ["2026-01-01", 172800.0, "2026-01-03"],
        ),
        (
            types.GenericAlias(slice, (date, timedelta)),
            slice(date(2026, 1, 1), timedelta(days=2), timedelta(days=3)),
            ["2026-01-01", 172800.0, 259200.0],
        ),
        (
            types.GenericAlias(slice, (date, date, timedelta)),
            slice(None, date(2026, 1, 2), timedelta(days=3)),
            [None, "2026-01-02", 259200.0],
        ),
    ),
)
def test_generic_slice(slice_type, value, dumped):
    assert BasicEncoder(slice_type).encode(value) == dumped
    assert BasicDecoder(slice_type).decode(dumped) == value


@pytest.mark.skipif(sys.version_info < (3, 15), reason="requires python 3.15")
def test_native_generic_slice():
    slice_type = slice[date, date, timedelta]
    value = slice(date(2026, 1, 1), date(2026, 1, 2), timedelta(days=3))
    dumped = ["2026-01-01", "2026-01-02", 259200.0]

    assert BasicEncoder(slice_type).encode(value) == dumped
    assert BasicDecoder(slice_type).decode(dumped) == value


@pytest.mark.skipif(sys.version_info < (3, 15), reason="requires python 3.15")
def test_generic_slice_with_resolved_type_var():
    T = TypeVar("T")

    @dataclass
    class GenericSlice(Generic[T]):
        value: slice[T]  # pragma: no cover

    @dataclass
    class DateSlice(GenericSlice[date], DataClassDictMixin):
        pass

    value = DateSlice(slice(date(2026, 1, 1), None, date(2026, 1, 3)))
    dumped = {"value": ["2026-01-01", None, "2026-01-03"]}

    assert value.to_dict() == dumped
    assert DateSlice.from_dict(dumped) == value
