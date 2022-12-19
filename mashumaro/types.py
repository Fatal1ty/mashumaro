import decimal
from typing import Any, List, Optional, Type, Union

from typing_extensions import Literal

from mashumaro.core.const import Sentinel


class SerializableType:
    __use_annotations__ = False

    def __init_subclass__(
        cls,
        use_annotations: Union[
            bool, Literal[Sentinel.MISSING]
        ] = Sentinel.MISSING,
        **kwargs: Any,
    ):
        if use_annotations is not Sentinel.MISSING:
            cls.__use_annotations__ = use_annotations

    def _serialize(self) -> Any:
        raise NotImplementedError

    @classmethod
    def _deserialize(cls, value: Any) -> Any:
        raise NotImplementedError


class GenericSerializableType:
    def _serialize(self, types: List[Type]) -> Any:
        raise NotImplementedError

    @classmethod
    def _deserialize(cls, value: Any, types: List[Type]) -> Any:
        raise NotImplementedError


class SerializationStrategy:
    def serialize(self, value: Any) -> Any:
        raise NotImplementedError

    def deserialize(self, value: Any) -> Any:
        raise NotImplementedError


class RoundedDecimal(SerializationStrategy):
    def __init__(
        self, places: Optional[int] = None, rounding: Optional[str] = None
    ):
        if places is not None:
            self.exp = decimal.Decimal((0, (1,), -places))
        else:
            self.exp = None  # type: ignore
        self.rounding = rounding

    def serialize(self, value: decimal.Decimal) -> str:
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
