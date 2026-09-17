from dataclasses import dataclass

import pytest

from mashumaro import DataClassDictMixin


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
