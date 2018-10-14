from base64 import encodebytes
from tests.entities.dataclasses import *
from tests.entities.custom import *
from collections import deque, ChainMap


def to_base64(data: bytes) -> str:
    return encodebytes(data).decode()


def dataclass_x(cls, x, dictionary, use_bytes=False):
    instance = cls(x)
    assert instance.to_dict(use_bytes=use_bytes) == dictionary
    assert cls.from_dict(dictionary, use_bytes=use_bytes) == instance


def test_data_class_with_int():
    x = 123
    dictionary = {'x': 123}
    dataclass_x(DataClassWithInt, x, dictionary)


def test_data_class_with_list():
    x = [1, 2, 3]
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithList, x, dictionary)


def test_data_class_with_generic_list():
    x = [1, 2, 3]
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithGenericList, x, dictionary)


def test_data_class_with_custom_list():
    x = CustomSerializableList.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableList, x, dictionary)


def test_data_class_with_deque():
    x = deque([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithDeque, x, dictionary)


def test_data_class_with_generic_deque():
    x = deque([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithGenericDeque, x, dictionary)


def test_data_class_with_custom_serializable_deque():
    x = CustomSerializableDeque.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableDeque, x, dictionary)


def test_data_class_with_tuple():
    x = (1, 2, 3)
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithTuple, x, dictionary)


def test_data_class_with_generic_tuple():
    x = (1, 2, 3)
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithGenericTuple, x, dictionary)


def test_data_class_with_custom_serializable_tuple():
    x = CustomSerializableTuple.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableTuple, x, dictionary)


def test_data_class_with_set():
    x = {1, 2, 3}
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithSet, x, dictionary)


def test_data_class_with_generic_set():
    x = {1, 2, 3}
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithGenericSet, x, dictionary)


def test_data_class_with_custom_serializable_set():
    x = CustomSerializableSet.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableSet, x, dictionary)


def test_data_class_with_abstract_set():
    x = {1, 2, 3}
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithAbstractSet, x, dictionary)


def test_data_class_with_abstract_mutable_set():
    x = {1, 2, 3}
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithAbstractMutableSet, x, dictionary)


def test_data_class_with_frozen_set():
    x = {1, 2, 3}
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithGenericFrozenSet, x, dictionary)


def test_data_class_with_custom_serializable_frozen_set():
    x = CustomSerializableFrozenSet.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableFrozenSet, x, dictionary)


def test_data_class_with_chain_map():
    x = ChainMap({'a': 1, 'b': 2}, {'c': 3, 'd': 4})
    dictionary = {'x': [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]}
    dataclass_x(DataClassWithChainMap, x, dictionary)


def test_data_class_with_generic_chain_map():
    x = ChainMap({'a': 1, 'b': 2}, {'c': 3, 'd': 4})
    dictionary = {'x': [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]}
    dataclass_x(DataClassWithGenericChainMap, x, dictionary)


def test_data_class_with_custom_serializable_chain_map():
    x = CustomSerializableChainMap.from_sequence(
        [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}])
    dictionary = {'x': [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]}
    dataclass_x(DataClassWithCustomSerializableChainMap, x, dictionary)


def test_data_class_with_dict():
    x = {'a': 1, 'b': 2}
    dictionary = {'x': {'a': 1, 'b': 2}}
    dataclass_x(DataClassWithDict, x, dictionary)


def test_data_class_with_generic_dict():
    x = {'a': 1, 'b': 2}
    dictionary = {'x': {'a': 1, 'b': 2}}
    dataclass_x(DataClassWithGenericDict, x, dictionary)


def test_data_class_with_custom_serializable_mapping():
    x = CustomSerializableMapping.from_mapping({'a': 1, 'b': 2})
    dictionary = {'x': {'a': 1, 'b': 2}}
    dataclass_x(DataClassWithCustomSerializableMapping, x, dictionary)


def test_data_class_with_abstract_mapping():
    x = {'a': 1, 'b': 2}
    dictionary = {'x': {'a': 1, 'b': 2}}
    dataclass_x(DataClassWithAbstractMapping, x, dictionary)


def test_data_class_with_abstract_mutable_mapping():
    x = {'a': 1, 'b': 2}
    dictionary = {'x': {'a': 1, 'b': 2}}
    dataclass_x(DataClassWithAbstractMutableMapping, x, dictionary)


def test_data_class_with_bytes():
    x = b'123'
    x_b64 = to_base64(b'123')
    inst = DataClassWithBytes(x)
    assert inst.to_dict(use_bytes=True) == {'x': x}
    assert inst.to_dict(use_bytes=False) == {'x': x_b64}
    assert DataClassWithBytes.from_dict({'x': x}, use_bytes=True) == inst
    assert DataClassWithBytes.from_dict({'x': x_b64}, use_bytes=False) == inst


def test_data_class_with_byte_array():
    x = bytearray(b'123')
    x_b64 = to_base64(b'123')
    inst = DataClassWithByteArray(x)
    assert inst.to_dict(use_bytes=True) == {'x': b'123'}
    assert inst.to_dict(use_bytes=False) == {'x': x_b64}
    assert DataClassWithByteArray.from_dict({'x': x}, use_bytes=True) == inst
    assert DataClassWithByteArray.from_dict(
        {'x': x_b64}, use_bytes=False) == inst


def test_data_class_with_custom_serializable_bytes():
    x = CustomSerializableBytes.from_bytes(b'123')
    x_b64 = to_base64(b'123')
    inst = DataClassWithCustomSerializableBytes(x)
    assert inst.to_dict(use_bytes=True) == {'x': b'123'}
    assert inst.to_dict(use_bytes=False) == {'x': x_b64}
    assert DataClassWithCustomSerializableBytes.from_dict(
        {'x': b'123'}, use_bytes=True) == inst
    assert DataClassWithCustomSerializableBytes.from_dict(
        {'x': x_b64}, use_bytes=False) == inst


def test_data_class_with_custom_serializable_byte_array():
    x = CustomSerializableByteArray.from_bytes(b'123')
    x_b64 = to_base64(b'123')
    inst = DataClassWithCustomSerializableByteArray(x)
    assert inst.to_dict(use_bytes=True) == {'x': b'123'}
    assert inst.to_dict(use_bytes=False) == {'x': x_b64}
    assert DataClassWithCustomSerializableByteArray.from_dict(
        {'x': b'123'}, use_bytes=True) == inst
    assert DataClassWithCustomSerializableByteArray.from_dict(
        {'x': x_b64}, use_bytes=False) == inst


def test_data_class_with_abstract_byte_string():
    x = b'123'
    x_b64 = to_base64(x)
    inst = DataClassWithAbstractByteString(x)
    assert inst.to_dict(use_bytes=True) == {'x': b'123'}
    assert inst.to_dict(use_bytes=False) == {'x': x_b64}
    assert DataClassWithAbstractByteString.from_dict(
        {'x': b'123'}, use_bytes=True) == inst
    assert DataClassWithAbstractByteString.from_dict(
        {'x': x_b64}, use_bytes=False) == inst


def test_data_class_with_string():
    x = '123'
    dictionary = {'x': x}
    dataclass_x(DataClassWithStr, x, dictionary)


def test_data_class_with_custom_serializable_sequence():
    x = CustomSerializableSequence.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableSequence, x, dictionary)


def test_data_class_with_custom_serializable_mutable_sequence():
    x = CustomSerializableMutableSequence.from_sequence([1, 2, 3])
    dictionary = {'x': [1, 2, 3]}
    dataclass_x(DataClassWithCustomSerializableMutableSequence, x, dictionary)


def test_data_class_with_abstract_sequence():
    x = [1, 2, 3]
    dictionary = {'x': x}
    dataclass_x(DataClassWithAbstractSequence, x, dictionary)


def test_data_class_with_abstract_mutable_sequence():
    x = [1, 2, 3]
    dictionary = {'x': x}
    dataclass_x(DataClassWithAbstractMutableSequence, x, dictionary)


def test_data_class_with_enum():
    x = MyEnum.a
    value = x.value
    inst = DataClassWithEnum(x)
    assert inst.to_dict(use_enum=True) == {'x': x}
    assert inst.to_dict(use_enum=False) == {'x': value}
    assert DataClassWithEnum.from_dict({'x': x}, use_enum=True) == inst
    assert DataClassWithEnum.from_dict({'x': value}, use_enum=False) == inst


def test_data_class_with_int_enum():
    x = MyIntEnum.a
    value = x.value
    inst = DataClassWithIntEnum(x)
    assert inst.to_dict(use_enum=True) == {'x': x}
    assert inst.to_dict(use_enum=False) == {'x': value}
    assert DataClassWithIntEnum.from_dict({'x': x}, use_enum=True) == inst
    assert DataClassWithIntEnum.from_dict({'x': value}, use_enum=False) == inst


def test_data_class_with_flag():
    x = MyFlag.a
    value = x.value
    inst = DataClassWithFlag(x)
    assert inst.to_dict(use_enum=True) == {'x': x}
    assert inst.to_dict(use_enum=False) == {'x': value}
    assert DataClassWithFlag.from_dict({'x': x}, use_enum=True) == inst
    assert DataClassWithFlag.from_dict({'x': value}, use_enum=False) == inst


def test_data_class_with_int_flag():
    x = MyIntFlag.a
    value = x.value
    inst = DataClassWithIntFlag(x)
    assert inst.to_dict(use_enum=True) == {'x': x}
    assert inst.to_dict(use_enum=False) == {'x': value}
    assert DataClassWithIntFlag.from_dict({'x': x}, use_enum=True) == inst
    assert DataClassWithIntFlag.from_dict({'x': value}, use_enum=False) == inst
