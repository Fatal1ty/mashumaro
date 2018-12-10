import json
from dataclasses import dataclass
from typing import List, Optional

from mashumaro import DataClassDictMixin


@dataclass
class NestedClass(DataClassDictMixin):
    z: str = 'z'


def test_encode_hook():

    def encode_hook(instance, out_dict):
        out_dict["one"] = 1
        return out_dict

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[NestedClass] = None

    ref_non_nested = {'x': None, 'one': 1}
    ref_nested = {'x': {'one': 1, 'z': 'z'}, 'one': 1}

    assert DataClass().to_dict(encode_hook=encode_hook) == ref_non_nested
    assert DataClass(NestedClass()).to_dict(encode_hook=encode_hook) == ref_nested


def test_decode_hook():

    def decode_hook(cls, out_dict):
        out_dict["z"] = 'some_other_value'
        return out_dict

    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[NestedClass] = None
        z: str = 'z'

    input_dict = {'x': {'z': 'z'}, 'z': 'z'}
    out_instance = DataClass.from_dict(input_dict, decode_hook=decode_hook)

    assert out_instance.z == 'some_other_value'
    assert out_instance.x.z == 'some_other_value'
