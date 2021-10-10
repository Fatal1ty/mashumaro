import collections
import collections.abc
import typing
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from mashumaro import DataClassDictMixin, DataClassJSONMixin
from mashumaro.meta.helpers import (
    get_class_that_defines_field,
    get_class_that_defines_method,
    get_generic_name,
    get_type_origin,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dataclass_dict_mixin_subclass,
    is_generic,
    is_init_var,
    is_type_var_any,
    resolve_type_vars,
    type_name,
)
from mashumaro.meta.macros import PEP_585_COMPATIBLE, PY_37, PY_37_MIN, PY_38
from mashumaro.serializer.base.metaprogramming import CodeBuilder

from .entities import (
    MyDataClass,
    MyGenericDataClass,
    MyGenericList,
    T,
    TAny,
    TInt,
    TIntStr,
)

TMyDataClass = typing.TypeVar("TMyDataClass", bound=MyDataClass)


def test_is_generic_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39_MIN", False):
                    with pytest.raises(NotImplementedError):
                        is_generic(int)


def test_is_class_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37_MIN", False):
            with pytest.raises(NotImplementedError):
                is_class_var(int)


def test_is_init_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38_MIN", False):
                with pytest.raises(NotImplementedError):
                    is_init_var(int)


def test_no_code_builder():
    with patch(
        "mashumaro.serializer.base.dict."
        "DataClassDictMixin.__init_subclass__",
        lambda: ...,
    ):

        @dataclass
        class DataClass(DataClassDictMixin):
            pass

        assert DataClass.from_dict({}) is None
        assert DataClass().to_dict() is None
        assert DataClass.__pre_deserialize__({}) is None
        assert DataClass.__post_deserialize__(DataClass()) is None
        assert DataClass().__pre_serialize__() is None
        assert DataClass().__post_serialize__({}) is None


def test_get_class_that_defines_method():
    class A:
        def foo(self):
            pass  # pragma no cover

        @classmethod
        def bar(cls):
            pass  # pragma no cover

        def foobar(self):
            pass  # pragma no cover

    class B(A):
        def foobar(self):
            pass  # pragma no cover

    assert get_class_that_defines_method("foo", B) == A
    assert get_class_that_defines_method("bar", B) == A
    assert get_class_that_defines_method("foobar", B) == B


def test_get_class_that_defines_field():
    @dataclass
    class A:
        x: int
        y: int
        z: int

    @dataclass
    class B(A):
        y: float
        z: int

    assert get_class_that_defines_field("x", B) == A
    assert get_class_that_defines_field("y", B) == B
    assert get_class_that_defines_field("z", B) == B


def test_get_unknown_declared_hook():
    builder = CodeBuilder(object)
    assert builder.get_declared_hook("unknown_name") is None


def test_is_dataclass_dict_mixin():
    assert is_dataclass_dict_mixin(DataClassDictMixin)
    assert not is_dataclass_dict_mixin(DataClassJSONMixin)


def test_is_dataclass_dict_mixin_subclass():
    assert is_dataclass_dict_mixin_subclass(DataClassDictMixin)
    assert is_dataclass_dict_mixin_subclass(DataClassJSONMixin)
    assert is_dataclass_dict_mixin_subclass(MyDataClass)


def test_is_type_var_any():
    assert is_type_var_any(TAny)
    assert not is_type_var_any(typing.Any)
    assert not is_type_var_any(TMyDataClass)


@pytest.mark.skipif(not (PY_37 or PY_38), reason="requires python 3.7..3.8")
def test_is_type_var_any_list_37_38():
    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    assert is_type_var_any(typing.List.__args__[0])


def test_type_name():
    assert type_name(TAny) == "typing.Any"
    assert type_name(TInt) == "int"
    assert type_name(TMyDataClass) == "tests.entities.MyDataClass"
    assert type_name(TIntStr) == "typing.Union[int, str]"
    assert type_name(typing.List[TInt]) == "typing.List[int]"
    assert type_name(typing.Tuple[int]) == "typing.Tuple[int]"
    assert type_name(typing.Set[int]) == "typing.Set[int]"
    assert type_name(typing.FrozenSet[int]) == "typing.FrozenSet[int]"
    assert type_name(typing.Deque[int]) == "typing.Deque[int]"
    assert type_name(typing.Dict[int, int]) == "typing.Dict[int, int]"
    assert type_name(typing.Mapping[int, int]) == "typing.Mapping[int, int]"
    assert (
        type_name(typing.MutableMapping[int, int])
        == "typing.MutableMapping[int, int]"
    )
    assert type_name(typing.Counter[int]) == "typing.Counter[int]"
    assert type_name(typing.ChainMap[int, int]) == "typing.ChainMap[int, int]"
    assert type_name(typing.Sequence[int]) == "typing.Sequence[int]"
    assert type_name(typing.Union[int, str]) == "typing.Union[int, str]"
    assert (
        type_name(typing.Union[int, typing.Any])
        == "typing.Union[int, typing.Any]"
    )
    if PY_37_MIN:
        assert (
            type_name(typing.OrderedDict[int, int])
            == "typing.OrderedDict[int, int]"
        )
    assert type_name(typing.Optional[int]) == "typing.Optional[int]"
    assert type_name(None) == "None"


@pytest.mark.skipif(not PEP_585_COMPATIBLE, reason="requires python 3.9+")
def test_type_name_pep_585():
    assert type_name(list[str]) == "list[str]"
    assert type_name(collections.deque[str]) == "collections.deque[str]"
    assert type_name(tuple[str]) == "tuple[str]"
    assert type_name(set[str]) == "set[str]"
    assert type_name(frozenset[str]) == "frozenset[str]"
    assert type_name(collections.abc.Set[str]) == "collections.abc.Set[str]"
    assert (
        type_name(collections.abc.MutableSet[str])
        == "collections.abc.MutableSet[str]"
    )
    assert type_name(collections.Counter[str]) == "collections.Counter[str]"
    assert (
        type_name(collections.abc.Sequence[str])
        == "collections.abc.Sequence[str]"
    )
    assert (
        type_name(collections.abc.MutableSequence[str])
        == "collections.abc.MutableSequence[str]"
    )
    assert (
        type_name(collections.ChainMap[str, str])
        == "collections.ChainMap[str, str]"
    )
    assert type_name(dict[str, str]) == "dict[str, str]"
    assert (
        type_name(collections.abc.Mapping[str, str])
        == "collections.abc.Mapping[str, str]"
    )
    assert (
        type_name(collections.OrderedDict[str, str])
        == "collections.OrderedDict[str, str]"
    )


def test_type_name_short():
    assert type_name(TAny, short=True) == "Any"
    assert type_name(TInt, short=True) == "int"
    assert type_name(TMyDataClass, short=True) == "MyDataClass"
    assert type_name(TIntStr, short=True) == "Union[int, str]"
    assert type_name(typing.List[TInt], short=True) == "List[int]"
    assert type_name(typing.Tuple[int], short=True) == "Tuple[int]"
    assert type_name(typing.Set[int], short=True) == "Set[int]"
    assert type_name(typing.FrozenSet[int], short=True) == "FrozenSet[int]"
    assert type_name(typing.Deque[int], short=True) == "Deque[int]"
    assert type_name(typing.Dict[int, int], short=True) == "Dict[int, int]"
    assert (
        type_name(typing.Mapping[int, int], short=True) == "Mapping[int, int]"
    )
    assert (
        type_name(typing.MutableMapping[int, int], short=True)
        == "MutableMapping[int, int]"
    )
    assert type_name(typing.Counter[int], short=True) == "Counter[int]"
    assert (
        type_name(typing.ChainMap[int, int], short=True)
        == "ChainMap[int, int]"
    )
    assert type_name(typing.Sequence[int], short=True) == "Sequence[int]"
    assert type_name(typing.Union[int, str], short=True) == "Union[int, str]"
    assert (
        type_name(typing.Union[int, typing.Any], short=True)
        == "Union[int, Any]"
    )
    if PY_37_MIN:
        assert (
            type_name(typing.OrderedDict[int, int], short=True)
            == "OrderedDict[int, int]"
        )
    assert type_name(typing.Optional[int], short=True) == "Optional[int]"
    assert type_name(None, short=True) == "None"


@pytest.mark.skipif(not PEP_585_COMPATIBLE, reason="requires python 3.9+")
def test_type_name_pep_585_short():
    assert type_name(list[str], short=True) == "list[str]"
    assert type_name(collections.deque[str], short=True) == "deque[str]"
    assert type_name(tuple[str], short=True) == "tuple[str]"
    assert type_name(set[str], short=True) == "set[str]"
    assert type_name(frozenset[str], short=True) == "frozenset[str]"
    assert type_name(collections.abc.Set[str], short=True) == "Set[str]"
    assert (
        type_name(collections.abc.MutableSet[str], short=True)
        == "MutableSet[str]"
    )
    assert type_name(collections.Counter[str], short=True) == "Counter[str]"
    assert (
        type_name(collections.abc.Sequence[str], short=True) == "Sequence[str]"
    )
    assert (
        type_name(collections.abc.MutableSequence[str], short=True)
        == "MutableSequence[str]"
    )
    assert (
        type_name(collections.ChainMap[str, str], short=True)
        == "ChainMap[str, str]"
    )
    assert type_name(dict[str, str], short=True) == "dict[str, str]"
    assert (
        type_name(collections.abc.Mapping[str, str], short=True)
        == "Mapping[str, str]"
    )
    assert (
        type_name(collections.OrderedDict[str, str], short=True)
        == "OrderedDict[str, str]"
    )


def test_get_type_origin():
    assert get_type_origin(typing.List[int]) == list
    assert get_type_origin(typing.List) == list
    assert get_type_origin(MyGenericDataClass[int]) == MyGenericDataClass
    assert get_type_origin(MyGenericDataClass) == MyGenericDataClass


def test_resolve_type_vars():
    @dataclass
    class A(typing.Generic[T]):
        x: T

    @dataclass
    class B(A[int]):
        pass

    resolved = resolve_type_vars(B)
    assert resolved[A] == {T: int}
    assert resolved[B] == {}


def test_get_generic_name():
    assert get_generic_name(typing.List[int]) == "typing.List"
    assert get_generic_name(typing.List[int], short=True) == "List"
    assert (
        get_generic_name(MyGenericDataClass[int])
        == "tests.entities.MyGenericDataClass"
    )
    assert (
        get_generic_name(MyGenericDataClass[int], short=True)
        == "MyGenericDataClass"
    )


def test_get_generic_collection_based_class_name():
    assert get_generic_name(MyGenericList, short=True) == "MyGenericList"
    assert get_generic_name(MyGenericList) == "tests.entities.MyGenericList"
    assert get_generic_name(MyGenericList[int], short=True) == "MyGenericList"
    assert (
        get_generic_name(MyGenericList[int]) == "tests.entities.MyGenericList"
    )
