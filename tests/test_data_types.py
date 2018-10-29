import collections
from enum import Enum
from datetime import datetime, date, time, timedelta
from dataclasses import dataclass
from typing import (
    Hashable,
    List,
    Deque,
    Tuple,
    Set,
    FrozenSet,
    MutableSet,
    ChainMap,
    Dict,
    Mapping,
    MutableMapping,
    Sequence,
)

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import UnserializableField, UnserializableDataError
from .utils import same_types
from .entities import (
    MyEnum,
    MyIntEnum,
    MyFlag,
    MyIntFlag,
    MyDataClass,
)

import pytest


class Fixture:
    INT = 123
    FLOAT = 1.23
    BOOL = True
    LIST = [1, 2, 3]
    TUPLE = (1, 2, 3)
    DEQUE = collections.deque([1, 2, 3])
    SET = {1, 2, 3}
    FROZEN_SET = frozenset([1, 2, 3])
    CHAIN_MAP = collections.ChainMap({'a': 1, 'b': 2}, {'c': 3, 'd': 4})
    MAPS_LIST = [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]
    DICT = {'a': 1, 'b': 2}
    BYTES = b'123'
    BYTES_BASE64 = 'MTIz\n'
    BYTE_ARRAY = bytearray(b'123')
    STR = '123'
    ENUM = MyEnum.a
    INT_ENUM = MyIntEnum.a
    FLAG = MyFlag.a
    INT_FLAG = MyIntFlag.a
    DATA_CLASS = MyDataClass(a=1, b=2)
    NONE = None
    DATETIME = datetime(2018, 10, 29, 12, 46, 55, 308495)
    DATE = DATETIME.date()
    TIME = DATETIME.time()
    TIMEDELTA = timedelta(3.14159265358979323846)


inner_values = [
    (int, Fixture.INT, Fixture.INT),
    (float, Fixture.FLOAT, Fixture.FLOAT),
    (bool, Fixture.BOOL, Fixture.BOOL),
    (List[int], Fixture.LIST, Fixture.LIST),
    (Deque[int], Fixture.DEQUE, Fixture.LIST),
    (Tuple[int], Fixture.TUPLE, Fixture.LIST),
    (Set[int], Fixture.SET, Fixture.LIST),
    (FrozenSet[int], Fixture.FROZEN_SET, Fixture.LIST),
    (ChainMap[str, int], Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (Dict[str, int], Fixture.DICT, Fixture.DICT),
    (Mapping[str, int], Fixture.DICT, Fixture.DICT),
    (MutableMapping[str, int], Fixture.DICT, Fixture.DICT),
    (Sequence[int], Fixture.LIST, Fixture.LIST),
    (bytes, Fixture.BYTES, Fixture.BYTES),
    (bytearray, Fixture.BYTE_ARRAY, Fixture.BYTE_ARRAY),
    (str, Fixture.STR, Fixture.STR),
    (MyEnum, Fixture.ENUM, Fixture.ENUM),
    (MyIntEnum, Fixture.INT_ENUM, Fixture.INT_ENUM),
    (MyFlag, Fixture.FLAG, Fixture.FLAG),
    (MyIntFlag, Fixture.INT_FLAG, Fixture.INT_FLAG),
    (MyDataClass, Fixture.DATA_CLASS, Fixture.DICT),
    (type(None), Fixture.NONE, Fixture.NONE),
    (datetime, Fixture.DATETIME, Fixture.DATETIME.isoformat()),
    (date, Fixture.DATE, Fixture.DATE.isoformat()),
    (time, Fixture.TIME, Fixture.TIME.isoformat()),
    (timedelta, Fixture.TIMEDELTA, Fixture.TIMEDELTA.total_seconds()),
]


hashable_inner_values = [
    (type_, value, value_dumped) for type_, value, value_dumped in inner_values
    if isinstance(value, Hashable) and isinstance(value_dumped, Hashable)
]


generic_sequence_types = [List, Deque, Tuple, Set, FrozenSet]
generic_mapping_types = [Dict, Mapping, MutableMapping]


unsupported_field_types = [
    list, collections.deque, tuple, set, frozenset, collections.ChainMap, dict]


x_factory_mapping = {
    List: list,
    Deque: collections.deque,
    Tuple: tuple,
    Set: set,
    FrozenSet: frozenset,
    MutableSet: set,
    Dict: lambda items: {k: v for k, v in items},
    Mapping: lambda items: {k: v for k, v in items},
    MutableMapping: lambda items: {k: v for k, v in items},
    ChainMap: lambda items: collections.ChainMap(*({k: v} for k, v in items))
}


# noinspection PyCallingNonCallable
def check_one_arg_generic(type_, value_info, use_bytes, use_enum):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: type_[x_type]

    x_factory = x_factory_mapping[type_]
    x = x_factory([x_value for _ in range(3)])
    instance = DataClass(x)
    if x_value_dumped is Fixture.BYTES:
        v_dumped = Fixture.BYTES if use_bytes else Fixture.BYTES_BASE64
    elif x_value_dumped is Fixture.BYTE_ARRAY:
        v_dumped = Fixture.BYTE_ARRAY if use_bytes else Fixture.BYTES_BASE64
    elif isinstance(x_value_dumped, Enum):
        v_dumped = x_value_dumped if use_enum else x_value_dumped.value
    else:
        v_dumped = x_value_dumped
    dumped = {'x': list(x_factory([v_dumped for _ in range(3)]))}
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x)


# noinspection PyCallingNonCallable
def check_two_args_generic(type_, key_info, value_info, use_bytes, use_enum):
    k_type, k_value, k_value_dumped = key_info
    v_type, v_value, v_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: type_[k_type, v_type]

    x_factory = x_factory_mapping[type_]
    x = x_factory([(k_value, v_value) for _ in range(3)])
    instance = DataClass(x)
    if k_value_dumped is Fixture.BYTES:
        k_dumped = Fixture.BYTES if use_bytes else Fixture.BYTES_BASE64
    elif k_value_dumped is Fixture.BYTE_ARRAY:
        k_dumped = Fixture.BYTE_ARRAY if use_bytes else Fixture.BYTES_BASE64
    elif isinstance(k_value_dumped, Enum):
        k_dumped = k_value_dumped if use_enum else k_value_dumped.value
    else:
        k_dumped = k_value_dumped
    if v_value_dumped is Fixture.BYTES:
        v_dumped = Fixture.BYTES if use_bytes else Fixture.BYTES_BASE64
    elif v_value_dumped is Fixture.BYTE_ARRAY:
        v_dumped = Fixture.BYTE_ARRAY if use_bytes else Fixture.BYTES_BASE64
    elif isinstance(v_value_dumped, Enum):
        v_dumped = v_value_dumped if use_enum else v_value_dumped.value
    else:
        v_dumped = v_value_dumped
    if type_ is ChainMap:
        dumped = {'x': x_factory([(k_dumped, v_dumped) for _ in range(3)]).maps}
    else:
        dumped = {'x': x_factory([(k_dumped, v_dumped) for _ in range(3)])}
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
def test_one_level(value_info, use_bytes, use_enum):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: x_type

    instance = DataClass(x_value)
    if x_value_dumped is Fixture.BYTES:
        v_dumped = Fixture.BYTES if use_bytes else Fixture.BYTES_BASE64
    elif x_value_dumped is Fixture.BYTE_ARRAY:
        v_dumped = Fixture.BYTE_ARRAY if use_bytes else Fixture.BYTES_BASE64
    elif isinstance(x_value_dumped, Enum):
        v_dumped = x_value_dumped if use_enum else x_value_dumped.value
    else:
        v_dumped = x_value_dumped
    dumped = {'x': v_dumped}
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    instance_dumped = instance.to_dict(use_bytes=use_bytes, use_enum=use_enum)
    instance_loaded = DataClass.from_dict(
        dumped, use_bytes=use_bytes, use_enum=use_enum)
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x_value)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
def test_with_generic_list(value_info, use_bytes, use_enum):
    check_one_arg_generic(List, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
def test_with_generic_deque(value_info, use_bytes, use_enum):
    check_one_arg_generic(Deque, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
def test_with_generic_tuple(value_info, use_bytes, use_enum):
    check_one_arg_generic(Tuple, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', hashable_inner_values)
def test_with_generic_set(value_info, use_bytes, use_enum):
    check_one_arg_generic(Set, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', hashable_inner_values)
def test_with_generic_frozenset(value_info, use_bytes, use_enum):
    check_one_arg_generic(FrozenSet, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', hashable_inner_values)
def test_with_generic_mutable_set(value_info, use_bytes, use_enum):
    check_one_arg_generic(MutableSet, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
@pytest.mark.parametrize('key_info', hashable_inner_values)
def test_with_generic_dict(key_info, value_info, use_bytes, use_enum):
    check_two_args_generic(Dict, key_info, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
@pytest.mark.parametrize('key_info', hashable_inner_values)
def test_with_generic_mapping(key_info, value_info, use_bytes, use_enum):
    check_two_args_generic(Mapping, key_info, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
@pytest.mark.parametrize('key_info', hashable_inner_values)
def test_with_generic_mutable_mapping(key_info, value_info,
                                      use_bytes, use_enum):
    check_two_args_generic(MutableMapping, key_info, value_info,
                           use_bytes, use_enum)


@pytest.mark.parametrize('use_enum', [True, False])
@pytest.mark.parametrize('use_bytes', [True, False])
@pytest.mark.parametrize('value_info', inner_values)
@pytest.mark.parametrize('key_info', hashable_inner_values)
def test_with_generic_chain_map(key_info, value_info, use_bytes, use_enum):
    check_two_args_generic(ChainMap, key_info, value_info, use_bytes, use_enum)


@pytest.mark.parametrize('x_type', unsupported_field_types)
@pytest.mark.parametrize('generic_type', generic_sequence_types)
def test_unsupported_generic_field_types(x_type, generic_type):
    with pytest.raises(UnserializableField):
        @dataclass
        class _(DataClassDictMixin):
            # noinspection PyTypeChecker
            x: generic_type[x_type]


@pytest.mark.parametrize('x_type', unsupported_field_types)
def test_unsupported_field_types(x_type):
    with pytest.raises(UnserializableField):
        @dataclass
        class _(DataClassDictMixin):
            # noinspection PyTypeChecker
            x: x_type


@pytest.mark.parametrize('generic_type', generic_mapping_types)
def test_data_class_as_mapping_key(generic_type):
    @dataclass
    class Key(DataClassDictMixin):
        pass
    with pytest.raises(UnserializableDataError):
        @dataclass
        class _(DataClassDictMixin):
            x: generic_type[Key, int]


def test_data_class_as_chain_map_key():
    @dataclass
    class Key(DataClassDictMixin):
        pass
    with pytest.raises(UnserializableDataError):
        @dataclass
        class _(DataClassDictMixin):
            x: ChainMap[Key, int]
