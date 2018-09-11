from typing import Mapping

from mashumaro.serializer.base.metaprogramming import add_from_dict, add_to_dict


class DataClassDictMixin:
    def __init_subclass__(cls, **kwargs):
        add_from_dict(cls)
        add_to_dict(cls)

    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, d: Mapping):
        pass


__all__ = [DataClassDictMixin]
