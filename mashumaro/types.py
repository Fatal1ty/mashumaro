import decimal


class SerializableType:
    def _serialize(self):
        raise NotImplementedError

    @classmethod
    def _deserialize(cls, value):
        raise NotImplementedError


class GenericSerializableType:
    def _serialize(self, types):
        raise NotImplementedError

    @classmethod
    def _deserialize(cls, value, types):
        raise NotImplementedError


class SerializationStrategy:
    def serialize(self, value):
        raise NotImplementedError

    def deserialize(self, value):
        raise NotImplementedError


class RoundedDecimal(SerializationStrategy):
    def __init__(self, places=None, rounding=None):
        if places is not None:
            self.exp = decimal.Decimal((0, (1,), -places))
        else:
            self.exp = None
        self.rounding = rounding

    def serialize(self, value) -> str:
        if self.exp:
            if self.rounding:
                return str(value.quantize(self.exp, rounding=self.rounding))
            else:
                return str(value.quantize(self.exp))
        else:
            return str(value)

    def deserialize(self, value: str) -> decimal.Decimal:
        return decimal.Decimal(str(value))


__all__ = [
    "SerializableType",
    "GenericSerializableType",
    "SerializationStrategy",
    "RoundedDecimal",
]
