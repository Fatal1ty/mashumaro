from dataclasses import Field, dataclass, field, fields
from typing import Any, Callable, Dict, MutableMapping

from mashumaro import DataClassDictMixin


# dataclass that inherits from MutableMapping
@dataclass
class BaseConfig(DataClassDictMixin, MutableMapping[str, Any]):
    __test__ = False
    _extra: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return self._extra[key]

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self._extra[key] = value

    def _content_iterator(self, include_condition: Callable[[Field], bool]):
        seen = set()
        for fld in fields(self):
            seen.add(fld.name)
            if include_condition(fld):
                yield fld.name
        for key in self._extra:
            if key not in seen:
                seen.add(key)
                yield key

    def __delitem__(self, key):
        if hasattr(self, key):
            raise Exception("Cannot delete built-inkeys")
        else:
            del self._extra[key]

    def __iter__(self):
        yield from self._content_iterator(include_condition=lambda f: True)

    def __len__(self):
        return len(fields(self)) + len(self._extra)


@dataclass
class TestConfig(BaseConfig):
    name: str = "test"


def test_mm():
    obj = TestConfig()
    assert obj

    dct = obj.to_dict()
    assert dct
