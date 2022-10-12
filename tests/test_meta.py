import collections
import collections.abc
import typing
from dataclasses import dataclass
from datetime import datetime

import pytest
import typing_extensions

from mashumaro import DataClassDictMixin
from mashumaro.core.const import (
    PEP_585_COMPATIBLE,
    PY_37,
    PY_37_MIN,
    PY_38,
    PY_38_MIN,
    PY_310_MIN,
)
from mashumaro.core.meta.builder import CodeBuilder
from mashumaro.core.meta.helpers import (
    get_args,
    get_class_that_defines_field,
    get_class_that_defines_method,
    get_generic_name,
    get_literal_values,
    get_type_origin,
    is_annotated,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dataclass_dict_mixin_subclass,
    is_dialect_subclass,
    is_generic,
    is_init_var,
    is_literal,
    is_new_type,
    is_optional,
    is_type_var_any,
    is_union,
    not_none_type_arg,
    resolve_type_vars,
    type_name,
)
from mashumaro.dialect import Dialect
from mashumaro.mixins.json import DataClassJSONMixin

from .entities import (
    MyDataClass,
    MyDatetimeNewType,
    MyEnum,
    MyFlag,
    MyGenericDataClass,
    MyGenericList,
    MyIntEnum,
    MyIntFlag,
    MyNativeStrEnum,
    MyStrEnum,
    T,
    TAny,
    TInt,
    TIntStr,
)

NoneType = type(None)

TMyDataClass = typing.TypeVar("TMyDataClass", bound=MyDataClass)


def test_is_generic_unsupported_python(mocker):
    mocker.patch("mashumaro.core.meta.helpers.PY_36", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_37", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_38", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_39_MIN", False)
    with pytest.raises(NotImplementedError):
        is_generic(int)


def test_is_class_var_unsupported_python(mocker):
    mocker.patch("mashumaro.core.meta.helpers.PY_36", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_37_MIN", False)
    with pytest.raises(NotImplementedError):
        is_class_var(int)


def test_is_init_var_unsupported_python(mocker):
    mocker.patch("mashumaro.core.meta.helpers.PY_36", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_37", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_38_MIN", False)
    with pytest.raises(NotImplementedError):
        is_init_var(int)


def test_is_literal_unsupported_python(mocker):
    mocker.patch("mashumaro.core.meta.helpers.PY_36", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_37", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_38", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_39_MIN", False)
    assert not is_literal(typing_extensions.Literal[1])


def test_get_literal_values_unsupported_python(mocker):
    mocker.patch("mashumaro.core.meta.helpers.PY_36", False)
    mocker.patch("mashumaro.core.meta.helpers.PY_37_MIN", False)
    with pytest.raises(NotImplementedError):
        get_literal_values(typing_extensions.Literal[1])


def test_no_code_builder(mocker):
    mocker.patch(
        "mashumaro.mixins.dict.DataClassDictMixin.__init_subclass__",
        lambda: ...,
    )

    @dataclass
    class DataClass(DataClassDictMixin):
        pass

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
            type_name(typing_extensions.OrderedDict[int, int])
            == "typing.OrderedDict[int, int]"
        )
    else:
        assert (
            type_name(typing_extensions.OrderedDict[int, int])
            == "typing_extensions.OrderedDict[int, int]"
        )
    assert type_name(typing.Optional[int]) == "typing.Optional[int]"
    assert type_name(typing.Union[None, int]) == "typing.Optional[int]"
    assert type_name(typing.Union[int, None]) == "typing.Optional[int]"
    assert type_name(None) == "None"
    assert type_name(NoneType) == "NoneType"
    assert type_name(NoneType, none_type_as_none=True) == "None"
    assert type_name(typing.List[NoneType]) == "typing.List[NoneType]"
    assert (
        type_name(typing.Union[int, str, None])
        == "typing.Union[int, str, None]"
    )
    assert type_name(typing.Optional[NoneType]) == "NoneType"

    if PY_310_MIN:
        assert type_name(int | None) == "typing.Optional[int]"
        assert type_name(None | int) == "typing.Optional[int]"
        assert type_name(int | str) == "typing.Union[int, str]"
    if PY_310_MIN:
        assert (
            type_name(MyDatetimeNewType) == "tests.entities.MyDatetimeNewType"
        )
    else:
        assert type_name(MyDatetimeNewType) == type_name(datetime)
    assert (
        type_name(typing_extensions.Annotated[TMyDataClass, None])
        == "tests.entities.MyDataClass"
    )


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
    assert (
        type_name(typing_extensions.OrderedDict[int, int], short=True)
        == "OrderedDict[int, int]"
    )
    assert type_name(typing.Optional[int], short=True) == "Optional[int]"
    assert type_name(typing.Union[None, int], short=True) == "Optional[int]"
    assert type_name(typing.Union[int, None], short=True) == "Optional[int]"
    assert type_name(None, short=True) == "None"
    assert type_name(NoneType, short=True) == "NoneType"
    assert type_name(NoneType, short=True, none_type_as_none=True) == "None"
    assert type_name(typing.List[NoneType], short=True) == "List[NoneType]"
    assert (
        type_name(typing.Union[int, str, None], short=True)
        == "Union[int, str, None]"
    )
    assert type_name(typing.Optional[NoneType], short=True) == "NoneType"

    if PY_310_MIN:
        assert type_name(int | None, short=True) == "Optional[int]"
        assert type_name(None | int, short=True) == "Optional[int]"
        assert type_name(int | str, short=True) == "Union[int, str]"
    if PY_310_MIN:
        assert type_name(MyDatetimeNewType, short=True) == "MyDatetimeNewType"
    else:
        assert type_name(MyDatetimeNewType, short=True) == type_name(
            datetime, short=True
        )
    assert (
        type_name(typing_extensions.Annotated[TMyDataClass, None], short=True)
        == "MyDataClass"
    )


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
    assert (
        get_type_origin(typing_extensions.Annotated[datetime, None])
        == datetime
    )


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


def test_is_dialect_subclass():
    class MyDialect(Dialect):
        pass

    assert is_dialect_subclass(Dialect)
    assert is_dialect_subclass(MyDialect)
    assert not is_dialect_subclass(123)


def test_is_union():
    t = typing.Optional[str]
    assert is_union(t)
    assert get_args(t) == (str, NoneType)
    t = typing.Union[str, None]
    assert is_union(t)
    assert get_args(t) == (str, NoneType)
    t = typing.Union[None, str]
    assert is_union(t)
    assert get_args(t) == (NoneType, str)


@pytest.mark.skipif(not PY_310_MIN, reason="requires python 3.10+")
def test_is_union_pep_604():
    t = str | None
    assert is_union(t)
    assert get_args(t) == (str, NoneType)
    t = None | str
    assert is_union(t)
    assert get_args(t) == (NoneType, str)


def test_is_optional():
    t = typing.Optional[str]
    assert is_optional(t)
    assert get_args(t) == (str, NoneType)
    t = typing.Union[str, None]
    assert is_optional(t)
    assert get_args(t) == (str, NoneType)
    t = typing.Union[None, str]
    assert is_optional(t)
    assert get_args(t) == (NoneType, str)


@pytest.mark.skipif(not PY_310_MIN, reason="requires python 3.10+")
def test_is_optional_pep_604():
    t = str | None
    assert is_optional(t)
    assert get_args(t) == (str, NoneType)
    t = None | str
    assert is_optional(t)
    assert get_args(t) == (NoneType, str)


def test_not_non_type_arg():
    assert not_none_type_arg((str, int)) == str
    assert not_none_type_arg((NoneType, int)) == int
    assert not_none_type_arg((str, NoneType)) == str
    assert not_none_type_arg((T, int), {T: NoneType}) == int


def test_is_new_type():
    assert is_new_type(typing.NewType("MyNewType", int))
    assert not is_new_type(int)


def test_is_annotated():
    assert is_annotated(typing_extensions.Annotated[datetime, None])
    assert not is_annotated(datetime)


def test_is_literal():
    assert is_literal(typing_extensions.Literal[1, 2, 3])
    assert not is_literal(typing_extensions.Literal)
    assert not is_literal([1, 2, 3])


def test_get_literal_values():
    assert get_literal_values(typing_extensions.Literal[1, 2, 3]) == (1, 2, 3)
    assert get_literal_values(
        typing_extensions.Literal[
            1, typing_extensions.Literal[typing_extensions.Literal[2], 3]
        ]
    ) == (1, 2, 3)


def test_type_name_literal():
    if PY_38_MIN:
        module_name = "typing"
    else:
        module_name = "typing_extensions"
    assert type_name(
        typing_extensions.Literal[
            1,
            "a",
            b"\x00",
            True,
            False,
            None,
            MyEnum.a,
            MyStrEnum.a,
            MyNativeStrEnum.a,
            MyIntEnum.a,
            MyFlag.a,
            MyIntFlag.a,
            typing_extensions.Literal[2, 3],
            typing_extensions.Literal[typing_extensions.Literal["b", "c"]],
        ]
    ) == (
        f"{module_name}.Literal[1, 'a', b'\\x00', True, False, None, "
        "tests.entities.MyEnum.a, tests.entities.MyStrEnum.a, "
        "tests.entities.MyNativeStrEnum.a, tests.entities.MyIntEnum.a, "
        "tests.entities.MyFlag.a, tests.entities.MyIntFlag.a, 2, 3, 'b', 'c']"
    )
