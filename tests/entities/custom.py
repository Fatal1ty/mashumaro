from collections import deque, ChainMap

from mashumaro.abc import SerializableSequence, SerializableMapping,\
    SerializableByteString
from tests.entities.abstract import *


class CustomSerializableList(list, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = []

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = list(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableList({str(self.x)})"


class CustomSerializableDeque(deque, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = deque()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = deque(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableDeque({str(self.x)})"


class CustomSerializableTuple(tuple, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = tuple()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = tuple(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableTuple({str(self.x)})"


class CustomSerializableSet(set, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = set()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = set(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableSet({str(self.x)})"


class CustomSerializableFrozenSet(set, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = frozenset()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = frozenset(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableFrozenSet({str(self.x)})"


class CustomSerializableChainMap(ChainMap, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = ChainMap()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = ChainMap(*seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableChainMap({str(self.x)})"


class CustomSerializableMapping(dict, SerializableMapping):
    def __init__(self):
        super().__init__()
        self.x = {}

    @classmethod
    def from_mapping(cls, mapping):
        inst = cls()
        inst.x = {**mapping}
        return inst

    def __repr__(self):
        return f"CustomSerializableMapping({str(self.x)})"


class CustomSerializableBytes(bytes, SerializableByteString):
    def __init__(self):
        super().__init__()
        self.x = bytes()

    @classmethod
    def from_bytes(cls, data: bytes):
        inst = cls()
        inst.x = bytes(data)
        return inst

    def to_bytes(self):
        return self.x

    def __repr__(self):
        return f"CustomSerializableBytes({str(self.x)})"


class CustomSerializableByteArray(bytes, SerializableByteString):
    def __init__(self):
        super().__init__()
        self.x = bytearray()

    @classmethod
    def from_bytes(cls, data: bytes):
        inst = cls()
        inst.x = bytearray(data)
        return inst

    def to_bytes(self):
        return bytes(self.x)

    def __repr__(self):
        return f"CustomSerializableByteArray({str(self.x)})"


class CustomSerializableSequence(AbstractSequence, SerializableSequence):
    def __init__(self):
        self.x = []

    def __iter__(self):
        return iter(self.x)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, item):
        return self.x[item]

    def foo(self):
        pass

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = list(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableSequence({str(self.x)})"


class CustomSerializableMutableSequence(AbstractMutableSequence,
                                        SerializableSequence):
    def __init__(self):
        self.x = []

    def __getitem__(self, item):
        return self.x[item]

    def __len__(self):
        return len(self.x)

    def __delitem__(self, key):
        del self.x[key]

    def __setitem__(self, key, value):
        self.x[key] = value

    def insert(self, index, obj):
        self.x.insert(index, obj)

    def foo(self):
        pass

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = list(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableMutableSequence({str(self.x)})"
