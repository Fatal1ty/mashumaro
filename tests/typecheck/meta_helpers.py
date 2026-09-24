from typing import Annotated, Any, Literal, Sequence

from typing_extensions import TypeForm, TypeVar, assert_type

from mashumaro.core.meta.helpers import (
    get_literal_values,
    get_type_annotations,
    get_type_var_default,
    is_annotated,
    is_builtin_type,
    is_class_var,
    is_dialect_subclass,
    is_final,
    is_generic,
    is_hashable_type,
    is_init_var,
    is_literal,
    is_named_tuple,
    is_new_type,
    is_not_required,
    is_optional,
    is_readonly,
    is_required,
    is_self,
    is_type_alias_type,
    is_type_var,
    is_type_var_any,
    is_type_var_tuple,
    is_typed_dict,
    is_union,
    is_unpack,
    is_variable_length_tuple,
)

T = TypeVar("T", default=int)


def check_annotation_predicates_accept_arbitrary_objects() -> None:
    value = object()

    assert_type(is_builtin_type(value), bool)
    assert_type(is_generic(value), bool)
    assert_type(is_typed_dict(value), bool)
    assert_type(is_readonly(value), bool)
    assert_type(is_named_tuple(value), bool)
    assert_type(is_new_type(value), bool)
    assert_type(is_union(value), bool)
    assert_type(is_optional(value), bool)
    assert_type(is_annotated(value), bool)
    assert_type(is_literal(value), bool)
    assert_type(is_type_var(value), bool)
    assert_type(is_type_var_any(value), bool)
    assert_type(is_class_var(value), bool)
    assert_type(is_final(value), bool)
    assert_type(is_init_var(value), bool)
    assert_type(is_dialect_subclass(value), bool)
    assert_type(is_self(value), bool)
    assert_type(is_required(value), bool)
    assert_type(is_not_required(value), bool)
    assert_type(is_unpack(value), bool)
    assert_type(is_type_var_tuple(value), bool)
    assert_type(is_type_alias_type(value), bool)


def check_type_form_helpers() -> None:
    assert_type(get_literal_values(Literal[1]), tuple[Any, ...])
    assert_type(
        get_type_annotations(Annotated[int, "metadata"]), Sequence[Any]
    )
    assert_type(is_variable_length_tuple(tuple[int, ...]), bool)
    assert_type(is_hashable_type(int), bool)
    assert_type(get_type_var_default(T), TypeForm)
