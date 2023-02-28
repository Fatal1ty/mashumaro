from dataclasses import dataclass

from typing_extensions import TypeVarTuple

from mashumaro.jsonschema.schema import Instance

Ts = TypeVarTuple("Ts")


def test_instance():
    @dataclass
    class DataClass:
        pass

    instance = Instance(int)
    assert instance.metadata == {}
    assert instance.holder_class is None

    instance = Instance(DataClass)
    assert instance.holder_class is DataClass
    assert instance.metadata == {}
