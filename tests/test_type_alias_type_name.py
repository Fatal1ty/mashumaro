import pytest

from mashumaro.core.meta.helpers import type_name
from tests.entities_pep_695 import (
    GenericAlias,
    Nested,
    RecursiveIntList,
)

type JSON = str | int | float | bool | dict[str, JSON] | list[JSON] | None
type A = int | list[B]
type B = str | list[A]


def test_type_name_recursive_type_alias_does_not_recurse_forever() -> None:
    # Must not raise RecursionError
    s = type_name(JSON, short=True)
    assert s == "JSON"


def test_type_name_mutual_recursive_type_aliases_does_not_recurse_forever() -> (
    None
):
    s = type_name(A, short=True)
    assert s == "A"


def test_type_name_bare_type_alias_returns_qualified_name() -> None:
    s = type_name(RecursiveIntList)
    assert s == f"{RecursiveIntList.__module__}.{RecursiveIntList.__name__}"


def test_type_name_bare_type_alias_short() -> None:
    assert type_name(RecursiveIntList, short=True) == "RecursiveIntList"


def test_type_name_parameterized_generic_alias() -> None:
    """type_name for GenericAlias[int] should return the qualified
    parameterized form, not an unwrapped structural type."""
    s = type_name(GenericAlias[int])
    assert "GenericAlias" in s
    assert "int" in s
    # Must NOT contain Optional[Any] — that was the old broken output
    assert "Any" not in s


def test_type_name_parameterized_generic_alias_short() -> None:
    s = type_name(GenericAlias[int], short=True)
    assert s == "GenericAlias[int]"


def test_type_name_recursive_generic_alias_no_recursion_error() -> None:
    """type_name for a recursive generic alias must not hit infinite recursion."""
    s = type_name(Nested[int])
    assert "Nested" in s
    assert "int" in s


def test_type_name_cross_module_alias_includes_module() -> None:
    """Aliases imported from another module should include the module path."""
    s = type_name(GenericAlias)
    assert "entities_pep_695" in s
    assert "GenericAlias" in s
