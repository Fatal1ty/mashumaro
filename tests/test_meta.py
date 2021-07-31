import typing
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from mashumaro import DataClassDictMixin, DataClassJSONMixin
from mashumaro.meta.helpers import (
    get_class_that_define_method,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dataclass_dict_mixin_subclass,
    is_generic,
    is_init_var,
    is_type_var_any,
    type_name,
)
from mashumaro.meta.macros import PY_37, PY_37_MIN, PY_38
from mashumaro.serializer.base.metaprogramming import CodeBuilder

from .entities import MyDataClass, TAny, TInt, TIntStr

TMyDataClass = typing.TypeVar("TMyDataClass", bound=MyDataClass)


def test_is_generic_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
                    with pytest.raises(NotImplementedError):
                        is_generic(int)


def test_is_class_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
                    with pytest.raises(NotImplementedError):
                        is_class_var(int)


def test_is_init_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
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


def test_get_class_that_define_method():
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

    assert get_class_that_define_method("foo", B) == A
    assert get_class_that_define_method("bar", B) == A
    assert get_class_that_define_method("foobar", B) == B


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
    assert is_type_var_any(List.__args__[0])


def test_type_name():
    assert type_name(TAny) == "Any"
    assert type_name(TInt) == "int"
    assert type_name(TMyDataClass) == "tests.entities.MyDataClass"
    assert type_name(TIntStr) == "Union[int, str]"
    assert type_name(typing.List[TInt]) == "List[int]"
    assert type_name(typing.Tuple[int]) == "Tuple[int]"
    assert type_name(typing.Set[int]) == "Set[int]"
    assert type_name(typing.FrozenSet[int]) == "FrozenSet[int]"
    assert type_name(typing.Deque[int]) == "Deque[int]"
    assert type_name(typing.Dict[int, int]) == "Dict[int, int]"
    assert type_name(typing.Mapping[int, int]) == "Mapping[int, int]"
    assert (
        type_name(typing.MutableMapping[int, int])
        == "MutableMapping[int, int]"
    )
    assert type_name(typing.Counter[int]) == "Counter[int]"
    assert type_name(typing.ChainMap[int, int]) == "ChainMap[int, int]"
    assert type_name(typing.Sequence[int]) == "Sequence[int]"
    assert type_name(typing.Union[int, str]) == "Union[int, str]"
    assert type_name(typing.Union[int, typing.Any]) == "Union[int, Any]"
    if PY_37_MIN:
        assert (
            type_name(typing.OrderedDict[int, int]) == "OrderedDict[int, int]"
        )
