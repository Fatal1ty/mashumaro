from abc import ABCMeta, abstractmethod
from typing import Sequence, Mapping


class SerializableSequence(metaclass=ABCMeta):

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_sequence(cls, seq: Sequence) -> 'SerializableSequence':
        pass


class SerializableMapping(metaclass=ABCMeta):

    __slots__ = ()

    @classmethod
    @abstractmethod
    def from_mapping(cls, mapping: Mapping) -> 'SerializableMapping':
        pass
