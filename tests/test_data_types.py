import collections
import collections.abc
import decimal
import fractions
import ipaddress
import os
import re
import uuid
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import (
    Path,
    PosixPath,
    PurePath,
    PurePosixPath,
    PureWindowsPath,
    WindowsPath,
)
from queue import Queue
from types import MappingProxyType
from typing import (
    Any,
    AnyStr,
    ChainMap,
    ClassVar,
    Counter,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Hashable,
    List,
    Mapping,
    MutableMapping,
    MutableSet,
    NewType,
    Optional,
    OrderedDict,
    Sequence,
    Set,
    Tuple,
)
from zoneinfo import ZoneInfo

import pytest
from typing_extensions import Final, LiteralString

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.codecs.basic import decode, encode
from mashumaro.config import BaseConfig
from mashumaro.exceptions import (
    InvalidFieldValue,
    MissingField,
    UnserializableDataError,
    UnserializableField,
)
from mashumaro.types import (
    GenericSerializableType,
    RoundedDecimal,
    SerializableType,
    SerializationStrategy,
)
from tests.entities import (
    MyUntypedNamedTupleWithDefaults,
    TDefaultInt,
    TypedDictWithReadOnly,
)

from .conftest import add_unpack_method
from .entities import (
    CustomPath,
    DataClassWithoutMixin,
    GenericNamedTuple,
    GenericSerializableList,
    GenericSerializableTypeDataClass,
    GenericTypedDict,
    MutableString,
    MyDataClass,
    MyDataClassWithUnion,
    MyDatetimeNewType,
    MyEnum,
    MyFlag,
    MyIntEnum,
    MyIntFlag,
    MyNamedTuple,
    MyNamedTupleWithDefaults,
    MyNamedTupleWithOptional,
    MyNativeStrEnum,
    MyStrEnum,
    MyUntypedNamedTuple,
    SerializableTypeDataClass,
    T,
    T_Optional_int,
    TAny,
    TInt,
    TIntStr,
    TMyDataClass,
    TypedDictOptionalKeys,
    TypedDictOptionalKeysWithOptional,
    TypedDictRequiredAndOptionalKeys,
    TypedDictRequiredKeys,
    TypedDictRequiredKeysWithOptional,
)
from .utils import same_types

NoneType = type(None)


class Fixture:
    T = 123
    T_INT = 123
    T_INT_STR = 123
    ANY = 123
    INT = 123
    FLOAT = 1.23
    BOOL = True
    LIST = [1, 2, 3]
    TUPLE = (1,)
    TUPLE_DUMPED = [1]
    DEQUE = collections.deque([1, 2, 3])
    SET = {1, 2, 3}
    FROZEN_SET = frozenset([1, 2, 3])
    CHAIN_MAP = collections.ChainMap({"a": 1, "b": 2}, {"c": 3, "d": 4})
    MAPS_LIST = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
    DICT = {"a": 1, "b": 2}
    ORDERED_DICT = collections.OrderedDict(a=1, b=2)
    DEFAULT_DICT = collections.defaultdict(int, a=1, b=2)
    MAPPING_PROXY = MappingProxyType(DICT)
    DEFAULT_NONE_DICT = collections.defaultdict(None, a=1, b=2)
    COUNTER: Counter[str] = collections.Counter(a=1, b=2)
    BYTES = b"123"
    BYTES_BASE64 = "MTIz\n"
    BYTE_ARRAY = bytearray(b"123")
    STR = "123"
    ENUM = MyEnum.a
    INT_ENUM = MyIntEnum.a
    STR_ENUM = MyStrEnum.a
    STR_ENUM_NATIVE = MyNativeStrEnum.a
    FLAG = MyFlag.a
    INT_FLAG = MyIntFlag.a
    DATA_CLASS = MyDataClass(a=1, b=2)
    T_DATA_CLASS = MyDataClass(a=1, b=2)
    DATA_CLASS_WITH_UNION = MyDataClassWithUnion(a=1, b=2)
    NONE = None
    DATETIME = datetime(2018, 10, 29, 12, 46, 55, 308495)
    DATETIME_STR = "2018-10-29T12:46:55.308495"
    DATE = DATETIME.date()
    DATE_STR = "2018-10-29"
    TIME = DATETIME.time()
    TIME_STR = "12:46:55.308495"
    TIMEDELTA = timedelta(3.14159265358979323846)
    TIMEZONE = timezone(timedelta(hours=3))
    UUID = uuid.UUID("3c25dd74-f208-46a2-9606-dd3919e975b7")
    UUID_STR = "3c25dd74-f208-46a2-9606-dd3919e975b7"
    IP4ADDRESS_STR = "127.0.0.1"
    IP4ADDRESS = ipaddress.IPv4Address(IP4ADDRESS_STR)
    IP6ADDRESS_STR = "::1"
    IP6ADDRESS = ipaddress.IPv6Address(IP6ADDRESS_STR)
    IP4NETWORK_STR = "127.0.0.0/8"
    IP4NETWORK = ipaddress.IPv4Network(IP4NETWORK_STR)
    IP6NETWORK_STR = "::/128"
    IP6NETWORK = ipaddress.IPv6Network(IP6NETWORK_STR)
    IP4INTERFACE_STR = "192.168.1.1/24"
    IP4INTERFACE = ipaddress.IPv4Interface(IP4INTERFACE_STR)
    IP6INTERFACE_STR = "::1/128"
    IP6INTERFACE = ipaddress.IPv6Interface(IP6INTERFACE_STR)
    DECIMAL = decimal.Decimal("1.33")
    DECIMAL_STR = "1.33"
    FRACTION = fractions.Fraction("1/3")
    FRACTION_STR = "1/3"
    MUTABLE_STRING = MutableString(STR)
    MUTABLE_STRING_STR = STR
    CUSTOM_PATH = CustomPath("/a/b/c")
    CUSTOM_PATH_STR = "/a/b/c"
    CUSTOM_SERIALIZE = "_FOOBAR_"
    GENERIC_SERIALIZABLE_LIST_INT = GenericSerializableList([1, 2, 3])
    GENERIC_SERIALIZABLE_LIST_STR = GenericSerializableList(["a", "b", "c"])
    LITERAL_STRING = "foo"
    PATTERN_STR = re.compile("[a-z]+")
    PATTERN_BYTES = re.compile(b"[a-z]+")


inner_values = [
    (T, Fixture.T, Fixture.T),
    (TInt, Fixture.T_INT, Fixture.T_INT),
    (TIntStr, Fixture.T_INT_STR, Fixture.T_INT_STR),
    (TDefaultInt, Fixture.T_INT, Fixture.T_INT),
    (Any, Fixture.ANY, Fixture.ANY),
    (TAny, Fixture.ANY, Fixture.ANY),
    (int, Fixture.INT, Fixture.INT),
    (float, Fixture.FLOAT, Fixture.FLOAT),
    (bool, Fixture.BOOL, Fixture.BOOL),
    (List[int], Fixture.LIST, Fixture.LIST),
    (list[int], Fixture.LIST, Fixture.LIST),
    (List, Fixture.LIST, Fixture.LIST),
    (list, Fixture.LIST, Fixture.LIST),
    (Deque[int], Fixture.DEQUE, Fixture.LIST),
    (collections.deque[int], Fixture.DEQUE, Fixture.LIST),
    (Deque, Fixture.DEQUE, Fixture.LIST),
    (collections.deque, Fixture.DEQUE, Fixture.LIST),
    (Tuple[int], Fixture.TUPLE, Fixture.TUPLE_DUMPED),
    (tuple[int], Fixture.TUPLE, Fixture.TUPLE_DUMPED),
    (Tuple, Fixture.TUPLE, Fixture.TUPLE_DUMPED),
    (tuple, Fixture.TUPLE, Fixture.TUPLE_DUMPED),
    (Set[int], Fixture.SET, Fixture.LIST),
    (set[int], Fixture.SET, Fixture.LIST),
    (Set, Fixture.SET, Fixture.LIST),
    (set, Fixture.SET, Fixture.LIST),
    (FrozenSet[int], Fixture.FROZEN_SET, Fixture.LIST),
    (frozenset[int], Fixture.FROZEN_SET, Fixture.LIST),
    (FrozenSet, Fixture.FROZEN_SET, Fixture.LIST),
    (frozenset, Fixture.FROZEN_SET, Fixture.LIST),
    (collections.abc.Set[int], Fixture.SET, Fixture.LIST),
    (collections.abc.Set, Fixture.SET, Fixture.LIST),
    (collections.abc.MutableSet[int], Fixture.SET, Fixture.LIST),
    (collections.abc.MutableSet, Fixture.SET, Fixture.LIST),
    (ChainMap[str, int], Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (
        collections.ChainMap[str, int],
        Fixture.CHAIN_MAP,
        Fixture.MAPS_LIST,
    ),
    (ChainMap, Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (collections.ChainMap, Fixture.CHAIN_MAP, Fixture.MAPS_LIST),
    (Dict[str, int], Fixture.DICT, Fixture.DICT),
    (dict[str, int], Fixture.DICT, Fixture.DICT),
    (Dict, Fixture.DICT, Fixture.DICT),
    (dict, Fixture.DICT, Fixture.DICT),
    (Mapping[str, int], Fixture.DICT, Fixture.DICT),
    (collections.abc.Mapping[str, int], Fixture.DICT, Fixture.DICT),
    (Mapping, Fixture.DICT, Fixture.DICT),
    (collections.abc.Mapping, Fixture.DICT, Fixture.DICT),
    (OrderedDict[str, int], Fixture.ORDERED_DICT, Fixture.DICT),
    (
        collections.OrderedDict[str, int],
        Fixture.ORDERED_DICT,
        Fixture.DICT,
    ),
    (OrderedDict, Fixture.ORDERED_DICT, Fixture.DICT),
    (collections.OrderedDict, Fixture.ORDERED_DICT, Fixture.DICT),
    (DefaultDict[str, int], Fixture.DEFAULT_DICT, Fixture.DICT),
    (
        collections.defaultdict[str, int],
        Fixture.DEFAULT_DICT,
        Fixture.DICT,
    ),
    (DefaultDict, Fixture.DEFAULT_NONE_DICT, Fixture.DICT),
    (collections.defaultdict, Fixture.DEFAULT_NONE_DICT, Fixture.DICT),
    (Counter[str], Fixture.COUNTER, Fixture.DICT),
    (collections.Counter[str], Fixture.COUNTER, Fixture.DICT),
    (Counter, Fixture.COUNTER, Fixture.DICT),
    (collections.Counter, Fixture.COUNTER, Fixture.DICT),
    (MutableMapping[str, int], Fixture.DICT, Fixture.DICT),
    (
        collections.abc.MutableMapping[str, int],
        Fixture.DICT,
        Fixture.DICT,
    ),
    (MutableMapping, Fixture.DICT, Fixture.DICT),
    (collections.abc.MutableMapping, Fixture.DICT, Fixture.DICT),
    (MappingProxyType[str, int], Fixture.MAPPING_PROXY, Fixture.DICT),
    (MappingProxyType, Fixture.MAPPING_PROXY, Fixture.DICT),
    (Sequence[int], Fixture.LIST, Fixture.LIST),
    (collections.abc.Sequence[int], Fixture.LIST, Fixture.LIST),
    (Sequence, Fixture.LIST, Fixture.LIST),
    (collections.abc.Sequence, Fixture.LIST, Fixture.LIST),
    (collections.abc.MutableSequence[int], Fixture.LIST, Fixture.LIST),
    (collections.abc.MutableSequence, Fixture.LIST, Fixture.LIST),
    (bytes, Fixture.BYTES, Fixture.BYTES_BASE64),
    (bytearray, Fixture.BYTE_ARRAY, Fixture.BYTES_BASE64),
    (str, Fixture.STR, Fixture.STR),
    (MyEnum, Fixture.ENUM, Fixture.ENUM.value),
    (MyStrEnum, Fixture.STR_ENUM, Fixture.STR_ENUM.value),
    (MyNativeStrEnum, Fixture.STR_ENUM_NATIVE, Fixture.STR_ENUM_NATIVE.value),
    (MyIntEnum, Fixture.INT_ENUM, Fixture.INT_ENUM.value),
    (MyFlag, Fixture.FLAG, Fixture.FLAG.value),
    (MyIntFlag, Fixture.INT_FLAG, Fixture.INT_FLAG.value),
    (MyDataClass, Fixture.DATA_CLASS, Fixture.DICT),
    (TMyDataClass, Fixture.T_DATA_CLASS, Fixture.DICT),
    (MyDataClassWithUnion, Fixture.DATA_CLASS_WITH_UNION, Fixture.DICT),
    (NoneType, Fixture.NONE, Fixture.NONE),
    (datetime, Fixture.DATETIME, Fixture.DATETIME_STR),
    (date, Fixture.DATE, Fixture.DATE_STR),
    (time, Fixture.TIME, Fixture.TIME_STR),
    (timedelta, Fixture.TIMEDELTA, Fixture.TIMEDELTA.total_seconds()),
    (timezone, Fixture.TIMEZONE, "UTC+03:00"),
    (ZoneInfo, ZoneInfo("Europe/Moscow"), "Europe/Moscow"),
    (uuid.UUID, Fixture.UUID, Fixture.UUID_STR),
    (ipaddress.IPv4Address, Fixture.IP4ADDRESS, Fixture.IP4ADDRESS_STR),
    (ipaddress.IPv6Address, Fixture.IP6ADDRESS, Fixture.IP6ADDRESS_STR),
    (ipaddress.IPv4Network, Fixture.IP4NETWORK, Fixture.IP4NETWORK_STR),
    (ipaddress.IPv6Network, Fixture.IP6NETWORK, Fixture.IP6NETWORK_STR),
    (ipaddress.IPv4Interface, Fixture.IP4INTERFACE, Fixture.IP4INTERFACE_STR),
    (ipaddress.IPv6Interface, Fixture.IP6INTERFACE, Fixture.IP6INTERFACE_STR),
    (decimal.Decimal, Fixture.DECIMAL, Fixture.DECIMAL_STR),
    (fractions.Fraction, Fixture.FRACTION, Fixture.FRACTION_STR),
    (MutableString, Fixture.MUTABLE_STRING, Fixture.MUTABLE_STRING_STR),
    (CustomPath, Fixture.CUSTOM_PATH, Fixture.CUSTOM_PATH_STR),
    (
        GenericSerializableList[int],
        Fixture.GENERIC_SERIALIZABLE_LIST_INT,
        [3, 4, 5],
    ),
    (
        GenericSerializableList[str],
        Fixture.GENERIC_SERIALIZABLE_LIST_STR,
        ["_a", "_b", "_c"],
    ),
    (MyDatetimeNewType, Fixture.DATETIME, Fixture.DATETIME_STR),
    (LiteralString, Fixture.LITERAL_STRING, Fixture.LITERAL_STRING),
    (re.Pattern, Fixture.PATTERN_STR, Fixture.PATTERN_STR.pattern),
    (
        re.Pattern[str],
        Fixture.PATTERN_STR,
        Fixture.PATTERN_STR.pattern,
    ),
    (
        re.Pattern[bytes],
        Fixture.PATTERN_BYTES,
        Fixture.PATTERN_BYTES.pattern,
    ),
]

if os.name == "posix":
    inner_values.extend(
        [
            (Path, Path("/a/b/c"), "/a/b/c"),
            (PurePath, PurePath("/a/b/c"), "/a/b/c"),
            (PosixPath, PosixPath("/a/b/c"), "/a/b/c"),
            (PurePosixPath, PurePosixPath("/a/b/c"), "/a/b/c"),
            (os.PathLike, PurePosixPath("/a/b/c"), "/a/b/c"),
        ]
    )
else:
    inner_values.extend(
        [
            (Path, Path("/a/b/c"), "\\a\\b\\c"),
            (PurePath, PurePath("/a/b/c"), "\\a\\b\\c"),
            (WindowsPath, WindowsPath("C:/Windows"), "C:\\Windows"),
            (
                PureWindowsPath,
                PureWindowsPath("C:/Program Files"),
                "C:\\Program Files",
            ),
            (os.PathLike, PureWindowsPath("/a/b/c"), "\\a\\b\\c"),
        ]
    )


hashable_inner_values = [
    (type_, value, value_dumped)
    for type_, value, value_dumped in inner_values
    if isinstance(value, Hashable) and isinstance(value_dumped, Hashable)
]


generic_sequence_types = [
    List,
    Deque,
    Tuple,
    Set,
    FrozenSet,
    list,
    collections.deque,
    tuple,
    set,
    frozenset,
    collections.abc.Set,
    collections.abc.MutableSet,
    collections.Counter,
    collections.abc.Sequence,
    collections.abc.MutableSequence,
]
generic_mapping_types = [
    Dict,
    Mapping,
    OrderedDict,
    DefaultDict,
    MutableMapping,
    collections.ChainMap,
    dict,
    collections.abc.Mapping,
    collections.OrderedDict,
    collections.defaultdict,
    collections.abc.MutableMapping,
]


unsupported_field_types = [Queue]
unsupported_typing_primitives = [AnyStr]


x_factory_mapping = {
    List: list,
    list: list,
    Deque: collections.deque,
    collections.deque: collections.deque,
    Tuple: tuple,
    tuple: tuple,
    Set: set,
    set: set,
    FrozenSet: frozenset,
    frozenset: frozenset,
    MutableSet: set,
    collections.abc.MutableSet: set,
    Dict: lambda items: {k: v for k, v in items},
    dict: lambda items: {k: v for k, v in items},
    Mapping: lambda items: {k: v for k, v in items},
    collections.abc.Mapping: lambda items: {k: v for k, v in items},
    MutableMapping: lambda items: {k: v for k, v in items},
    collections.abc.MutableMapping: lambda items: {k: v for k, v in items},
    OrderedDict: lambda items: {k: v for k, v in items},
    collections.OrderedDict: lambda items: {k: v for k, v in items},
    DefaultDict: lambda items: {k: v for k, v in items},
    collections.defaultdict: lambda items: {k: v for k, v in items},
    Counter: lambda items: collections.Counter({k: v for k, v in items}),
    collections.Counter: lambda items: collections.Counter(
        {k: v for k, v in items}
    ),
    ChainMap: lambda items: collections.ChainMap(*({k: v} for k, v in items)),
    collections.ChainMap: lambda items: collections.ChainMap(
        *({k: v} for k, v in items)
    ),
}


# noinspection PyCallingNonCallable
def check_collection_generic(type_, value_info, x_values_number=3):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: type_[x_type]

    x_factory = x_factory_mapping[type_]
    x = x_factory([x_value for _ in range(x_values_number)])
    instance = DataClass(x)
    dumped = {
        "x": list(x_factory([x_value_dumped for _ in range(x_values_number)]))
    }
    instance_dumped = instance.to_dict()
    instance_loaded = DataClass.from_dict(dumped)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x)


# noinspection PyCallingNonCallable
def check_mapping_generic(type_, key_info, value_info):
    k_type, k_value, k_value_dumped = key_info
    v_type, v_value, v_value_dumped = value_info

    if type_ is Counter:
        x_type = type_[k_type]
    else:
        x_type = type_[k_type, v_type]

    @dataclass
    class DataClass(DataClassDictMixin):
        x: x_type

    x_factory = x_factory_mapping[type_]
    if type_ is Counter:
        x = x_factory([(k_value, 1) for _ in range(3)])
    else:
        x = x_factory([(k_value, v_value) for _ in range(3)])
    instance = DataClass(x)
    k_dumped = k_value_dumped
    v_dumped = v_value_dumped
    if type_ is ChainMap:
        dumped = {
            "x": x_factory([(k_dumped, v_dumped) for _ in range(3)]).maps
        }
    elif type_ is Counter:
        dumped = {"x": x_factory([(k_dumped, 1) for _ in range(3)])}
    else:
        dumped = {"x": x_factory([(k_dumped, v_dumped) for _ in range(3)])}
    instance_dumped = instance.to_dict()
    instance_loaded = DataClass.from_dict(dumped)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x)


@pytest.mark.parametrize("value_info", inner_values)
def test_one_level(value_info):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: x_type

    instance = DataClass(x_value)
    dumped = {"x": x_value_dumped}
    instance_dumped = instance.to_dict()
    instance_loaded = DataClass.from_dict(dumped)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x_value)


@pytest.mark.parametrize("value_info", inner_values)
def test_with_generic_list(value_info):
    check_collection_generic(List, value_info)


@pytest.mark.parametrize("value_info", inner_values)
def test_with_generic_deque(value_info):
    check_collection_generic(Deque, value_info)


@pytest.mark.parametrize("value_info", inner_values)
def test_with_generic_tuple(value_info):
    check_collection_generic(Tuple, value_info, 1)


@pytest.mark.parametrize("value_info", hashable_inner_values)
def test_with_generic_set(value_info):
    check_collection_generic(Set, value_info)


@pytest.mark.parametrize("value_info", hashable_inner_values)
def test_with_generic_frozenset(value_info):
    check_collection_generic(FrozenSet, value_info)


@pytest.mark.parametrize("value_info", hashable_inner_values)
def test_with_generic_mutable_set(value_info):
    check_collection_generic(MutableSet, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_dict(key_info, value_info):
    check_mapping_generic(Dict, key_info, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_mapping(key_info, value_info):
    check_mapping_generic(Mapping, key_info, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_ordered_dict(key_info, value_info):
    check_mapping_generic(OrderedDict, key_info, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_counter(key_info, value_info):
    check_mapping_generic(Counter, key_info, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_mutable_mapping(key_info, value_info):
    check_mapping_generic(MutableMapping, key_info, value_info)


@pytest.mark.parametrize("value_info", inner_values)
@pytest.mark.parametrize("key_info", hashable_inner_values)
def test_with_generic_chain_map(key_info, value_info):
    check_mapping_generic(ChainMap, key_info, value_info)


@pytest.mark.parametrize("x_type", unsupported_field_types)
@pytest.mark.parametrize("generic_type", generic_sequence_types)
def test_unsupported_generic_field_types(x_type, generic_type):
    with pytest.raises(UnserializableField):

        @dataclass
        class _(DataClassDictMixin):
            # noinspection PyTypeChecker
            x: generic_type[x_type]

    with add_unpack_method:
        with pytest.raises(UnserializableField):

            @dataclass
            class _(DataClassDictMixin):
                # noinspection PyTypeChecker
                x: generic_type[x_type]


@pytest.mark.parametrize("x_type", unsupported_typing_primitives)
@pytest.mark.parametrize("generic_type", generic_sequence_types)
def test_unsupported_generic_typing_primitives(x_type, generic_type):
    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            # noinspection PyTypeChecker
            x: generic_type[x_type]

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                # noinspection PyTypeChecker
                x: generic_type[x_type]


@pytest.mark.parametrize("x_type", unsupported_field_types)
def test_unsupported_field_types(x_type):
    with pytest.raises(UnserializableField):

        @dataclass
        class _(DataClassDictMixin):
            x: x_type

    with add_unpack_method:
        with pytest.raises(UnserializableField):

            @dataclass
            class _(DataClassDictMixin):
                x: x_type


@pytest.mark.parametrize("x_type", unsupported_typing_primitives)
def test_unsupported_typing_primitives(x_type):
    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            x: x_type

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                x: x_type


@pytest.mark.parametrize("generic_type", generic_mapping_types)
def test_data_class_as_mapping_key(generic_type):
    @dataclass
    class Key(DataClassDictMixin):
        pass

    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            x: generic_type[Key, int]

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                x: generic_type[Key, int]


def test_data_class_as_mapping_key_for_counter():
    @dataclass
    class Key(DataClassDictMixin):
        pass

    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            x: Counter[Key]

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                x: Counter[Key]


def test_data_class_as_chain_map_key():
    @dataclass
    class Key(DataClassDictMixin):
        pass

    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            x: ChainMap[Key, int]

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                x: ChainMap[Key, int]


@pytest.mark.parametrize("value_info", inner_values)
def test_with_any(value_info):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Any

    x = value_info[1]
    dumped = {"x": x}
    instance = DataClass(x)
    instance_dumped = instance.to_dict()
    instance_loaded = DataClass.from_dict(dumped)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x)


@pytest.mark.parametrize("value_info", inner_values)
def test_with_optional(value_info):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[x_type] = None

    for instance in [DataClass(x_value), DataClass()]:
        if instance.x is None:
            v_dumped = None
        else:
            v_dumped = x_value_dumped
        dumped = {"x": v_dumped}
        instance_dumped = instance.to_dict()
        instance_loaded = DataClass.from_dict(dumped)
        assert instance_dumped == dumped
        assert instance_loaded == instance
        assert same_types(instance_dumped, dumped)
        assert same_types(instance_loaded.x, instance.x)


def test_raises_missing_field():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

    with pytest.raises(MissingField):
        DataClass.from_dict({})


def test_empty_dataclass():
    @dataclass
    class DataClass(DataClassDictMixin):
        pass

    assert DataClass().to_dict() == {}
    assert type(DataClass.from_dict({})) is DataClass
    assert DataClass.from_dict({}).__dict__ == {}


def test_weird_field_type():
    with pytest.raises(UnserializableDataError):

        @dataclass
        class _(DataClassDictMixin):
            x: 123

    with add_unpack_method:
        with pytest.raises(UnserializableDataError):

            @dataclass
            class _(DataClassDictMixin):
                x: 123


@pytest.mark.parametrize(
    "rounding", [None, decimal.ROUND_UP, decimal.ROUND_DOWN]
)
@pytest.mark.parametrize("places", [None, 1, 2])
def test_rounded_decimal(places, rounding):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: decimal.Decimal

        class Config(BaseConfig):
            serialization_strategy = {
                decimal.Decimal: RoundedDecimal(places, rounding)
            }

    digit = decimal.Decimal(0.35)
    if places is not None:
        exp = decimal.Decimal((0, (1,), -places))
        quantized = digit.quantize(exp, rounding)
    else:
        quantized = digit
    assert DataClass(digit).to_dict() == {"x": str(quantized)}
    assert DataClass.from_dict({"x": str(quantized)}) == DataClass(x=quantized)


def test_serializable_type():
    with pytest.raises(NotImplementedError):
        # noinspection PyTypeChecker
        SerializableType._serialize(None)
    with pytest.raises(NotImplementedError):
        SerializableType._deserialize(None)


def test_serialization_strategy():
    with pytest.raises(NotImplementedError):
        # noinspection PyTypeChecker
        SerializationStrategy.serialize(None, None)
    with pytest.raises(NotImplementedError):
        # noinspection PyTypeChecker
        SerializationStrategy.deserialize(None, None)


def test_class_vars():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: ClassVar[int] = None

    assert DataClass().to_dict() == {}
    assert DataClass.from_dict({}) == DataClass()


def test_final():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Final[int] = 42

    assert DataClass().to_dict() == {"x": 42}
    assert DataClass(42).to_dict() == {"x": 42}
    assert DataClass(33).to_dict() == {"x": 33}
    assert DataClass.from_dict({}) == DataClass()
    assert DataClass.from_dict({"x": 42}) == DataClass()
    assert DataClass.from_dict({"x": 33}) == DataClass(33)


def test_init_vars():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: InitVar[int] = None
        y: int = None

        def __post_init__(self, x: int):
            if self.y is None and x is not None:
                self.y = x

    assert DataClass().to_dict() == {"y": None}
    assert DataClass(x=1).to_dict() == {"y": 1}
    assert DataClass.from_dict({}) == DataClass()
    assert DataClass.from_dict({"x": 1}) == DataClass()


def test_dataclass_with_defaults():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        y: int = 1

    assert DataClass.from_dict({"x": 0}) == DataClass(x=0, y=1)


def test_dataclass_with_field_and_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(default=1)

    assert DataClass.from_dict({}) == DataClass(x=1)
    assert DataClass().to_dict() == {"x": 1}


def test_dataclass_with_field_and_no_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(metadata={})

    with pytest.raises(MissingField):
        assert DataClass.from_dict({})


def test_dataclass_with_field_and_default_factory():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: List[str] = field(default_factory=list)

    assert DataClass.from_dict({}) == DataClass(x=[])
    assert DataClass().to_dict() == {"x": []}


def test_derived_dataclass_with_ancestors_defaults():
    @dataclass
    class A:
        x: int
        y: int = 1

    @dataclass
    class B(A, DataClassDictMixin):
        z: int = 3

    @dataclass
    class C(B, DataClassDictMixin):
        y: int = 4

    @dataclass
    class D(C):
        pass

    assert B.from_dict({"x": 0}) == B(x=0, y=1, z=3)
    assert C.from_dict({"x": 0}) == C(x=0, y=4, z=3)
    assert D.from_dict({"x": 0}) == D(x=0, y=4, z=3)


def test_derived_dataclass_with_ancestors_and_field_with_default():
    @dataclass
    class A:
        x: int = field(default=1)

    @dataclass
    class B(A, DataClassDictMixin):
        y: int = field(default=2)

    @dataclass
    class C(B, DataClassDictMixin):
        z: int = field(default=3)

    @dataclass
    class D(C):
        pass

    assert B.from_dict({}) == B(x=1, y=2)
    assert C.from_dict({}) == C(x=1, y=2, z=3)
    assert D.from_dict({}) == D(x=1, y=2, z=3)


def test_derived_dataclass_with_ancestors_and_field_with_default_factory():
    @dataclass
    class A:
        x: List[int] = field(default_factory=lambda: [1])

    @dataclass
    class B(A, DataClassDictMixin):
        y: List[int] = field(default_factory=lambda: [2])

    @dataclass
    class C(B, DataClassDictMixin):
        z: List[int] = field(default_factory=lambda: [3])

    @dataclass
    class D(C):
        pass

    assert B.from_dict({}) == B(x=[1], y=[2])
    assert C.from_dict({}) == C(x=[1], y=[2], z=[3])
    assert D.from_dict({}) == D(x=[1], y=[2], z=[3])


def test_invalid_field_value_deserialization():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "bad_value"})


def test_invalid_field_value_deserialization_with_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = 1

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "bad_value"})


def test_invalid_field_value_deserialization_with_rounded_decimal():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: decimal.Decimal

        class Config(BaseConfig):
            serialization_strategy = {decimal.Decimal: RoundedDecimal()}

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "bad_value"})


def test_invalid_field_value_deserialization_with_rounded_decimal_with_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: decimal.Decimal = Fixture.DECIMAL

        class Config(BaseConfig):
            serialization_strategy = {decimal.Decimal: RoundedDecimal()}

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "bad_value"})


@pytest.mark.parametrize(
    "value_info",
    [
        v
        for v in inner_values
        if v[0] not in [MyDataClass, NoneType, MutableString]
    ],
)
def test_serialize_deserialize_options(value_info):
    x_type, x_value, x_value_dumped = value_info

    @dataclass
    class DataClass(DataClassDictMixin):
        x: x_type = field(
            metadata={
                "serialize": lambda v: Fixture.CUSTOM_SERIALIZE,
                "deserialize": lambda v: (
                    x_value
                    if v == Fixture.CUSTOM_SERIALIZE
                    else f"!{Fixture.CUSTOM_SERIALIZE}"
                ),
            }
        )

    instance = DataClass(x_value)
    v_dumped = Fixture.CUSTOM_SERIALIZE
    dumped = {"x": v_dumped}
    instance_dumped = instance.to_dict()
    instance_loaded = DataClass.from_dict(dumped)
    assert instance_dumped == dumped
    assert instance_loaded == instance
    assert same_types(instance_dumped, dumped)
    assert same_types(instance_loaded.x, x_value)


def test_dataclass_field_without_mixin():
    @dataclass
    class DataClass(DataClassDictMixin):
        p: DataClassWithoutMixin

    obj = DataClass(DataClassWithoutMixin(42))
    assert DataClass.from_dict({"p": {"i": "42"}}) == obj
    assert obj.to_dict() == {"p": {"i": 42}}


def test_serializable_type_dataclass():
    @dataclass
    class DataClass(DataClassDictMixin):
        s: SerializableTypeDataClass

    s_value = SerializableTypeDataClass(a=9, b=9)
    assert DataClass.from_dict({"s": {"a": 10, "b": 10}}) == DataClass(s_value)
    assert DataClass(s_value).to_dict() == {"s": {"a": 10, "b": 10}}


def test_optional_inside_collection():
    @dataclass
    class DataClass(DataClassDictMixin):
        l: List[Optional[int]]
        d: Dict[Optional[int], Optional[int]]

    d = {"l": [1, None, 2], "d": {1: 1, 2: None, None: 3}}
    o = DataClass.from_dict(d)
    assert o == DataClass(l=[1, None, 2], d={1: 1, 2: None, None: 3})
    assert o.to_dict() == d


def test_bound_type_var_inside_collection():
    @dataclass
    class DataClass(DataClassDictMixin):
        l: List[T_Optional_int]
        d: Dict[T_Optional_int, T_Optional_int]

    d = {"l": [1, None, 2], "d": {1: 1, 2: None, None: 3}}
    o = DataClass.from_dict(d)
    assert o == DataClass(l=[1, None, 2], d={1: 1, 2: None, None: 3})
    assert o.to_dict() == d


def test_generic_serializable_type():
    with pytest.raises(NotImplementedError):
        # noinspection PyTypeChecker
        GenericSerializableType._serialize(None, None)
    with pytest.raises(NotImplementedError):
        GenericSerializableType._deserialize(None, None)


def test_generic_serializable_type_dataclass():
    @dataclass
    class DataClass(DataClassDictMixin):
        s: GenericSerializableTypeDataClass

    s_value = GenericSerializableTypeDataClass(a=9, b=9)
    assert DataClass.from_dict({"s": {"a": 10, "b": 10}}) == DataClass(s_value)
    assert DataClass(s_value).to_dict() == {"s": {"a": 10, "b": 10}}


def test_dataclass_with_different_tuples():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Tuple
        c: Tuple[int]
        d: Tuple[int, float, int]
        e: Tuple[int, ...]

    obj = DataClass(a=(1, "2", 3.0), c=(1,), d=(1, 2.0, 3), e=(1, 2, 3))
    assert (
        DataClass.from_dict(
            {
                "a": [1, "2", 3.0],
                "c": [1, 2, 3],
                "d": ["1", "2.0", "3"],
                "e": [1, 2, 3],
            }
        )
        == obj
    )
    assert obj.to_dict() == {
        "a": [1, "2", 3.0],
        "c": [1],
        "d": [1, 2.0, 3],
        "e": [1, 2, 3],
    }


def test_dataclass_with_empty_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Tuple[()]

    obj = DataClass(x=())
    assert (
        DataClass.from_dict(
            {
                "x": [1, 2, 3],
            }
        )
        == obj
    )
    assert obj.to_dict() == {
        "x": [],
    }


def test_dataclass_with_typed_dict_required_keys():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictRequiredKeys

    for data in ({}, {"int": 1}, {"float": 1.0}):
        with pytest.raises(InvalidFieldValue):
            DataClass.from_dict({"x": data})

    obj = DataClass(x={"int": 1, "float": 2.0})
    assert (
        DataClass.from_dict({"x": {"int": "1", "float": "2.0", "str": "str"}})
        == obj
    )
    assert obj.to_dict() == {"x": {"int": 1, "float": 2.0}}


def test_dataclass_with_typed_dict_optional_keys():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictOptionalKeys

    for data in ({}, {"int": 1}, {"float": 1.0}):
        assert DataClass.from_dict({"x": data}) == DataClass(x=data)

    obj = DataClass(x={"int": 1, "float": 2.0})
    assert (
        DataClass.from_dict({"x": {"int": "1", "float": "2.0", "str": "str"}})
        == obj
    )
    assert obj.to_dict() == {"x": {"int": 1, "float": 2.0}}


def test_dataclass_with_typed_dict_required_and_optional_keys():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictRequiredAndOptionalKeys

    for data in (
        {},
        {"str": "str"},
        {"int": 1},
        {"float": 1.0},
        {"int": 1, "str": "str"},
        {"float": 1.0, "str": "str"},
    ):
        with pytest.raises(InvalidFieldValue):
            DataClass.from_dict({"x": data})

    assert DataClass.from_dict(
        {"x": {"int": "1", "float": "2.0", "unknown": "unknown"}}
    ) == DataClass(x={"int": 1, "float": 2.0})
    assert DataClass.from_dict(
        {"x": {"int": "1", "float": "2.0", "str": "str"}}
    ) == DataClass(x={"int": 1, "float": 2.0, "str": "str"})
    assert DataClass(x={"int": 1, "float": 2.0}).to_dict() == {
        "x": {"int": 1, "float": 2.0}
    }
    assert DataClass(x={"int": 1, "float": 2.0, "str": "str"}).to_dict() == {
        "x": {"int": 1, "float": 2.0, "str": "str"}
    }


def test_dataclass_with_typed_dict_with_read_only_key():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictWithReadOnly

    assert DataClass.from_dict({"x": {"x": "42"}}) == DataClass({"x": 42})
    assert DataClass({"x": 42}).to_dict() == {"x": {"x": 42}}


def test_dataclass_with_named_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyNamedTuple

    obj = DataClass(x=MyNamedTuple(1, 2.0))
    assert DataClass.from_dict({"x": ["1", "2.0"]}) == obj
    assert obj.to_dict() == {"x": [1, 2.0]}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": ["1", "2.0"]}) == obj
    assert encoder.encode(obj) == {"x": [1, 2.0]}


def test_dataclass_with_named_tuple_with_defaults():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyNamedTupleWithDefaults

    obj = DataClass(x=MyNamedTupleWithDefaults())
    assert DataClass.from_dict({"x": ["1"]}) == obj
    assert obj.to_dict() == {"x": [1, 2.0]}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": ["1"]}) == obj
    assert encoder.encode(obj) == {"x": [1, 2.0]}


def test_dataclass_with_untyped_named_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyUntypedNamedTuple

    obj = DataClass(x=MyUntypedNamedTuple("1", "2.0"))
    assert DataClass.from_dict({"x": ["1", "2.0"]}) == obj
    assert obj.to_dict() == {"x": ["1", "2.0"]}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": ["1", "2.0"]}) == obj
    assert encoder.encode(obj) == {"x": ["1", "2.0"]}


def test_dataclass_with_untyped_named_tuple_with_defaults():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyUntypedNamedTupleWithDefaults

    obj = DataClass(x=MyUntypedNamedTupleWithDefaults(i="1"))
    assert DataClass.from_dict({"x": ["1"]}) == obj
    assert obj.to_dict() == {"x": ["1", 2.0]}


def test_data_class_with_none():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: None
        y: NoneType
        z: List[None]

    obj = DataClass(x=None, y=None, z=[None])
    assert DataClass.from_dict({"x": None, "y": None, "z": [None]}) == obj
    assert DataClass.from_dict({"x": 42, "y": "foo", "z": ["bar"]}) == obj
    assert obj.to_dict() == {"x": None, "y": None, "z": [None]}


def test_data_class_with_new_type_overridden():
    MyStr = NewType("MyStr", str)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: str
        y: MyStr

        class Config(BaseConfig):
            serialization_strategy = {
                str: {
                    "serialize": lambda x: f"str_{x}",
                    "deserialize": lambda x: x[4:],
                },
                MyStr: {
                    "serialize": lambda x: f"MyStr_{x}",
                    "deserialize": lambda x: x[6:],
                },
            }

    instance = DataClass("a", MyStr("b"))
    assert DataClass.from_dict({"x": "str_a", "y": "MyStr_b"}) == instance
    assert instance.to_dict() == {"x": "str_a", "y": "MyStr_b"}


def test_tuple_with_optional():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Tuple[Optional[int], int] = field(default_factory=lambda: (None, 7))

    assert DataClass.from_dict({"x": [None, 42]}) == DataClass((None, 42))
    assert DataClass((None, 42)).to_dict() == {"x": [None, 42]}
    assert DataClass.from_dict({}) == DataClass((None, 7))
    assert DataClass().to_dict() == {"x": [None, 7]}


def test_tuple_with_optional_and_ellipsis():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Tuple[Optional[int], ...] = field(default_factory=lambda: (None, 7))

    assert DataClass.from_dict({"x": [None, 42]}) == DataClass((None, 42))
    assert DataClass((None, 42)).to_dict() == {"x": [None, 42]}
    assert DataClass.from_dict({}) == DataClass((None, 7))
    assert DataClass().to_dict() == {"x": [None, 7]}


def test_named_tuple_with_optional():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyNamedTupleWithOptional = field(
            default_factory=lambda: MyNamedTupleWithOptional(None, 7)
        )

    assert DataClass.from_dict({"x": [None, 42]}) == DataClass(
        MyNamedTupleWithOptional(None, 42)
    )
    assert DataClass(MyNamedTupleWithOptional(None, 42)).to_dict() == {
        "x": [None, 42]
    }
    assert DataClass.from_dict({}) == DataClass(
        MyNamedTupleWithOptional(None, 7)
    )
    assert DataClass().to_dict() == {"x": [None, 7]}


def test_unbound_generic_named_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericNamedTuple

    obj = DataClass(GenericNamedTuple("2023-01-22", 42))
    assert DataClass.from_dict({"x": ["2023-01-22", "42"]}) == obj
    assert obj.to_dict() == {"x": ["2023-01-22", 42]}


def test_bound_generic_named_tuple():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericNamedTuple[date]

    obj = DataClass(GenericNamedTuple(date(2023, 1, 22), 42))
    assert DataClass.from_dict({"x": ["2023-01-22", "42"]}) == obj
    assert obj.to_dict() == {"x": ["2023-01-22", 42]}


def test_typed_dict_required_keys_with_optional():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictRequiredKeysWithOptional

    obj = DataClass({"x": None, "y": 42})
    assert DataClass.from_dict({"x": {"x": None, "y": 42}}) == obj
    assert obj.to_dict() == {"x": {"x": None, "y": 42}}

    obj = DataClass({"x": 33, "y": 42})
    assert DataClass.from_dict({"x": {"x": 33, "y": 42}}) == obj
    assert obj.to_dict() == {"x": {"x": 33, "y": 42}}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": {"x": 33, "y": 42}}) == obj
    assert encoder.encode(obj) == {"x": {"x": 33, "y": 42}}


def test_typed_dict_optional_keys_with_optional():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: TypedDictOptionalKeysWithOptional

    obj = DataClass({"x": None, "y": 42})
    assert DataClass.from_dict({"x": {"x": None, "y": 42}}) == obj
    assert obj.to_dict() == {"x": {"x": None, "y": 42}}

    obj = DataClass({"x": 33, "y": 42})
    assert DataClass.from_dict({"x": {"x": 33, "y": 42}}) == obj
    assert obj.to_dict() == {"x": {"x": 33, "y": 42}}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": {"x": 33, "y": 42}}) == obj
    assert encoder.encode(obj) == {"x": {"x": 33, "y": 42}}


def test_unbound_generic_typed_dict():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericTypedDict

    obj = DataClass({"x": "2023-01-22", "y": 42})
    assert DataClass.from_dict({"x": {"x": "2023-01-22", "y": "42"}}) == obj
    assert obj.to_dict() == {"x": {"x": "2023-01-22", "y": 42}}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": {"x": "2023-01-22", "y": "42"}}) == obj
    assert encoder.encode(obj) == {"x": {"x": "2023-01-22", "y": 42}}


def test_bound_generic_typed_dict():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericTypedDict[date]

    obj = DataClass({"x": date(2023, 1, 22), "y": 42})
    assert DataClass.from_dict({"x": {"x": "2023-01-22", "y": "42"}}) == obj
    assert obj.to_dict() == {"x": {"x": "2023-01-22", "y": 42}}

    decoder = BasicDecoder(DataClass)
    encoder = BasicEncoder(DataClass)
    assert decoder.decode({"x": {"x": "2023-01-22", "y": "42"}}) == obj
    assert encoder.encode(obj) == {"x": {"x": "2023-01-22", "y": 42}}


def test_dataclass_with_init_false_field():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(init=False)

        def __post_init__(self):
            self.x = 42

    obj = DataClass()
    assert obj.to_dict() == {"x": 42}
    assert DataClass.from_dict({"x": 42}) == obj
    assert DataClass.from_dict({}) == obj


def test_dataclass_with_non_optional_none_value():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        y: int = None
        z: int = 42

    with pytest.raises(InvalidFieldValue) as e:
        DataClass.from_dict({"x": None})
    assert e.value.field_name == "x"

    obj = DataClass(x=42)
    assert DataClass.from_dict({"x": 42}) == obj
    assert obj.to_dict() == {"x": 42, "y": None, "z": 42}


def test_dataclass_with_optional_list_with_optional_ints():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[List[Optional[int]]]

    obj = DataClass(x=[42, None])
    assert DataClass.from_dict({"x": [42, None]}) == obj
    assert obj.to_dict() == {"x": [42, None]}


def test_dataclass_with_default_nan_and_inf_with_omit_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: float = float("nan")
        b: float = float("inf")
        c: float = float("-inf")

        class Config(BaseConfig):
            omit_default = True

    assert DataClass().to_dict() == {}
    assert DataClass(float("nan"), float("inf"), float("-inf")).to_dict() == {}
    assert (
        DataClass(float("nan"), float("+inf"), float("-inf")).to_dict() == {}
    )
    assert DataClass(float("inf"), float("-inf"), float("+inf")).to_dict() == {
        "a": float("inf"),
        "b": float("-inf"),
        "c": float("+inf"),
    }


def test_dataclass_with_default_int_flag_omit_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: MyIntFlag = MyIntFlag.a
        b: MyIntFlag = MyIntFlag.b

        class Config(BaseConfig):
            omit_default = True

    assert DataClass().to_dict() == {}
    assert DataClass(MyIntFlag.a, MyIntFlag.b).to_dict() == {}


@pytest.mark.parametrize("value_info", inner_values)
def test_decoder(value_info):
    x_type, x_value, x_value_dumped = value_info
    decoder = BasicDecoder(x_type)
    assert decoder.decode(x_value_dumped) == x_value
    assert decode(x_value_dumped, x_type) == x_value


@pytest.mark.parametrize("value_info", inner_values)
def test_encoder(value_info):
    x_type, x_value, x_value_dumped = value_info
    encoder = BasicEncoder(x_type)
    assert encoder.encode(x_value) == x_value_dumped
    assert encode(x_value, x_type) == x_value_dumped
