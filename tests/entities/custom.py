from collections import deque, ChainMap

from mashumaro.abc import SerializableSequence, SerializableMapping
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


class CustomSerializableBytes(bytes, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = bytes()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = bytes(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableBytes({str(self.x)})"


class CustomSerializableByteArray(bytes, SerializableSequence):
    def __init__(self):
        super().__init__()
        self.x = bytearray()

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = bytearray(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableByteArray({str(self.x)})"


class CustomSerializableSequence(AbstractSequence, SerializableSequence):
    def __init__(self):
        self.x = []

    def __getitem__(self, item):
        pass

    def __len__(self):
        pass

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
        pass

    def __len__(self):
        pass

    def __delitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def insert(self):
        pass

    def foo(self):
        pass

    @classmethod
    def from_sequence(cls, seq):
        inst = cls()
        inst.x = list(seq)
        return inst

    def __repr__(self):
        return f"CustomSerializableMutableSequence({str(self.x)})"
