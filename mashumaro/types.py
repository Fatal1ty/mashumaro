from abc import ABC, abstractmethod
import decimal


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


class RoundedDecimal(SerializationStrategy):
    def __init__(self, places=None, rounding=None):
        if places is not None:
            self.exp = decimal.Decimal((0, (1,), -places))
        else:
            self.exp = None
        self.rounding = rounding

    def _serialize(self, value) -> str:
        if self.exp:
            if self.rounding:
                return str(value.quantize(self.exp, rounding=self.rounding))
            else:
                return str(value.quantize(self.exp))
        else:
            return str(value)

    def _deserialize(self, value: str) -> decimal.Decimal:
        return decimal.Decimal(str(value))


__all__ = [
    'SerializableType',
    'SerializationStrategy',
    'RoundedDecimal',
]
