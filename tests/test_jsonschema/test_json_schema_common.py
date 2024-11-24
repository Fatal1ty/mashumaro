import pytest

from mashumaro.config import BaseConfig
from mashumaro.jsonschema.models import (
    JSONSchemaStringFormat,
    _deserialize_json_schema_instance_format,
)
from mashumaro.jsonschema.schema import Instance


def test_instance_get_configs():
    instance = Instance(int)
    assert instance.get_owner_config() is BaseConfig
    assert instance.get_self_config() is BaseConfig

    derived = instance.derive()
    assert derived.get_self_config() is instance.get_self_config()


def test_deserialize_json_schema_instance_format():
    assert (
        _deserialize_json_schema_instance_format("email")
        is JSONSchemaStringFormat.EMAIL
    )
    with pytest.raises(ValueError):
        assert _deserialize_json_schema_instance_format("foobar")
