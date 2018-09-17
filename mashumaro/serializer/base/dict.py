from typing import Mapping

from mashumaro.serializer.base.metaprogramming import CodeBuilder


class DataClassDictMixin:
    def __init_subclass__(cls, **kwargs):
        builder = CodeBuilder(cls)
        builder.add_from_dict()
        builder.add_to_dict()

    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, d: Mapping):
        pass


__all__ = [DataClassDictMixin]
