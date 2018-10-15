import collections
from typing import List, Deque, Tuple, Set, FrozenSet, ChainMap, Dict
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from tests.entities.custom import (
    CustomSerializableList,
    CustomSerializableDeque,
    CustomSerializableTuple,
    CustomSerializableSet,
    CustomSerializableFrozenSet,
    CustomSerializableChainMap,
    CustomSerializableMapping,
    CustomSerializableBytes,
    CustomSerializableByteArray,
    CustomSerializableSequence,
    CustomSerializableMutableSequence,
)
from tests.entities.abstract import (
    AbstractSet,
    AbstractMutableSet,
    AbstractMapping,
    AbstractMutableMapping,
    AbstractByteString,
    AbstractSequence,
    AbstractMutableSequence,
)
from tests.entities.enums import (
    MyEnum,
    MyIntEnum,
    MyFlag,
    MyIntFlag,
)

import pytest


class Fixture:
    INT = 123
    LIST = [1, 2, 3]
    TUPLE = (1, 2, 3)
    DEQUE = collections.deque([1, 2, 3])
    SET = {1, 2, 3}
    FROZEN_SET = frozenset()
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

    S_LIST = CustomSerializableList.from_sequence(LIST)
    S_DEQUE = CustomSerializableDeque.from_sequence(LIST)
    S_TUPLE = CustomSerializableTuple.from_sequence(TUPLE)
    S_SET = CustomSerializableSet.from_sequence(LIST)
    S_FROZEN_SET = CustomSerializableFrozenSet.from_sequence(LIST)
    S_CHAIN_MAP = CustomSerializableChainMap.from_maps(MAPS_LIST)
    S_DICT = CustomSerializableMapping.from_mapping(DICT)
    S_BYTES = CustomSerializableBytes.from_bytes(BYTES)
    S_BYTE_ARRAY = CustomSerializableByteArray.from_bytes(BYTES)
    S_SEQUENCE = CustomSerializableSequence.from_sequence(LIST)
    S_MUT_SEQUENCE = CustomSerializableMutableSequence.from_sequence(LIST)


inner_values = [
    (int, Fixture.INT, Fixture.INT),
    (list, Fixture.LIST, Fixture.LIST),
    (List[int], Fixture.LIST, Fixture.LIST),
    (CustomSerializableList, Fixture.S_LIST, Fixture.LIST),

    (collections.deque, Fixture.DEQUE, Fixture.LIST),
    (Deque[int], Fixture.DEQUE, Fixture.LIST),
    (CustomSerializableDeque, Fixture.S_DEQUE, Fixture.LIST),

    (tuple, Fixture.TUPLE, Fixture.LIST),
    (Tuple[int], Fixture.TUPLE, Fixture.LIST),
    (CustomSerializableTuple, Fixture.S_TUPLE, Fixture.LIST),

    (set, Fixture.SET, Fixture.LIST),
    (Set[int], Fixture.SET, Fixture.LIST),
    (CustomSerializableSet, Fixture.S_SET, Fixture.LIST),
    (AbstractSet, Fixture.SET, Fixture.LIST),
    (AbstractMutableSet, Fixture.SET, Fixture.LIST),
    (frozenset, Fixture.FROZEN_SET, Fixture.LIST),
    (FrozenSet[int], Fixture.FROZEN_SET, Fixture.LIST),
    (CustomSerializableFrozenSet, Fixture.S_FROZEN_SET, Fixture.LIST),

    (collections.ChainMap, Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (ChainMap[str, int], Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (CustomSerializableChainMap, Fixture.S_CHAIN_MAP, Fixture.MAPS_LIST),

    (dict, Fixture.DICT, Fixture.DICT),
    (Dict[str, int], Fixture.DICT, Fixture.DICT),
    (CustomSerializableMapping, Fixture.S_DICT, Fixture.DICT),
    (AbstractMapping, Fixture.DICT, Fixture.DICT),
    (AbstractMutableMapping, Fixture.DICT, Fixture.DICT),

    (bytes, Fixture.BYTES, Fixture.BYTES),
    (bytearray, Fixture.BYTE_ARRAY, Fixture.BYTES),
    (CustomSerializableBytes, Fixture.S_BYTES, Fixture.BYTES),
    (CustomSerializableByteArray, Fixture.S_BYTE_ARRAY, Fixture.BYTES),
    (AbstractByteString, Fixture.BYTES, Fixture.BYTES),
    (str, Fixture.STR, Fixture.STR),

    (CustomSerializableSequence, Fixture.S_SEQUENCE, Fixture.LIST),
    (CustomSerializableMutableSequence, Fixture.S_MUT_SEQUENCE, Fixture.LIST),
    (AbstractSequence, Fixture.LIST, Fixture.LIST),
    (AbstractMutableSequence, Fixture.LIST, Fixture.LIST),

    (MyEnum, Fixture.ENUM, Fixture.ENUM.value),
    (MyIntEnum, Fixture.INT_ENUM, Fixture.INT_ENUM.value),
    (MyFlag, Fixture.FLAG, Fixture.FLAG.value),
    (MyIntFlag, Fixture.INT_FLAG, Fixture.INT_FLAG.value),
]


def check_one_arg_generic(type_, inner_type, inner_value, inner_value_dumped):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: type_[inner_type]

    instance = DataClass(collections.deque([inner_value for _ in range(3)]))
    if inner_value_dumped == Fixture.BYTES:
        dumped_bytes = {'x': [Fixture.BYTES for _ in range(3)]}
        dumped_base64 = {'x': [Fixture.BYTES_BASE64 for _ in range(3)]}
        assert instance.to_dict(use_bytes=True) == dumped_bytes
        assert instance.to_dict(use_bytes=False) == dumped_base64
    else:
        dumped = {'x': [inner_value_dumped for _ in range(3)]}
        assert instance.to_dict() == dumped


@pytest.mark.parametrize(
    ('inner_type', 'inner_value', 'inner_value_dumped'), inner_values)
def test_with_generic_list(inner_type, inner_value, inner_value_dumped):
    check_one_arg_generic(List, inner_type, inner_value, inner_value_dumped)


@pytest.mark.parametrize(
    ('inner_type', 'inner_value', 'inner_value_dumped'), inner_values)
def test_with_generic_deque(inner_type, inner_value, inner_value_dumped):
    check_one_arg_generic(Deque, inner_type, inner_value, inner_value_dumped)


@pytest.mark.parametrize(
    ('inner_type', 'inner_value', 'inner_value_dumped'), inner_values)
def test_with_generic_tuple(inner_type, inner_value, inner_value_dumped):
    check_one_arg_generic(Tuple, inner_type, inner_value, inner_value_dumped)


@pytest.mark.parametrize(
    ('inner_type', 'inner_value', 'inner_value_dumped'), inner_values)
def test_with_generic_set(inner_type, inner_value, inner_value_dumped):
    check_one_arg_generic(Set, inner_type, inner_value, inner_value_dumped)


@pytest.mark.parametrize(
    ('inner_type', 'inner_value', 'inner_value_dumped'), inner_values)
def test_with_generic_frozenset(inner_type, inner_value, inner_value_dumped):
    check_one_arg_generic(FrozenSet, inner_type, inner_value,
                          inner_value_dumped)
