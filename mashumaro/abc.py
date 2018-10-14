from abc import ABCMeta, abstractmethod
from typing import Sequence, Mapping


class SerializableSequence(metaclass=ABCMeta):

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_sequence(cls, seq: Sequence) -> 'SerializableSequence':
        pass

    @abstractmethod
    def to_sequence(self) -> Sequence:
        pass


class SerializableMapping(metaclass=ABCMeta):

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_mapping(cls, mapping: Mapping) -> 'SerializableMapping':
        pass

    @abstractmethod
    def to_mapping(self) -> Mapping:
        pass


class SerializableByteString(metaclass=ABCMeta):

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes):
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass
