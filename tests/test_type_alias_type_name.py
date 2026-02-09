import pytest

from mashumaro.core.meta.helpers import type_name

type JSON = str | int | float | bool | dict[str, JSON] | list[JSON] | None
type A = int | list[B]
type B = str | list[A]


def test_type_name_recursive_type_alias_does_not_recurse_forever() -> None:
    # Must not raise RecursionError
    s = type_name(JSON, short=True)
    assert "JSON" in s


def test_type_name_mutual_recursive_type_aliases_does_not_recurse_forever() -> None:
    s = type_name(A, short=True)
    assert "A" in s
