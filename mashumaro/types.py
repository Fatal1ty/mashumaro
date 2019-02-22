from abc import ABC, abstractmethod


class SerializableType(ABC):
    @abstractmethod
    def _serialize(self):
        pass

    @classmethod
    @abstractmethod
    def _deserialize(cls, value):
        pass


class SerializationStrategy(ABC):
    @abstractmethod
    def _serialize(self, value):
        pass

    @abstractmethod
    def _deserialize(self, value):
        pass


__all__ = [
    'SerializableType',
    'SerializationStrategy',
]
