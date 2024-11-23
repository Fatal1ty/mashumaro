from dataclasses import dataclass
from typing import Optional

import pytest

from mashumaro.jsonschema.builder import JSONSchemaBuilder, build_json_schema
from mashumaro.jsonschema.models import (
    Context,
    JSONSchema,
    JSONSchemaInstanceType,
)
from mashumaro.jsonschema.plugins import BasePlugin, DocstringDescriptionPlugin
from mashumaro.jsonschema.schema import Instance


class ThirdPartyType:
    pass


@dataclass
class DataClassWithDocstring:
    """Here is the docstring"""

    x: int


@dataclass
class DataClassWithoutDocstring:
    x: int


def test_basic_plugin():
    assert build_json_schema(int, plugins=[BasePlugin()]) == JSONSchema(
        type=JSONSchemaInstanceType.INTEGER
    )


def test_plugin_with_not_implemented_error():
    class NotImplementedErrorPlugin(BasePlugin):
        def get_schema(
            self,
            instance: Instance,
            ctx: Context,
            schema: Optional[JSONSchema] = None,
        ) -> Optional[JSONSchema]:
            raise NotImplementedError

    assert build_json_schema(
        int, plugins=[NotImplementedErrorPlugin()]
    ) == JSONSchema(type=JSONSchemaInstanceType.INTEGER)
    assert JSONSchemaBuilder(plugins=[NotImplementedErrorPlugin()]).build(
        int
    ) == JSONSchema(type=JSONSchemaInstanceType.INTEGER)


@pytest.mark.parametrize(
    ("obj", "docstring"),
    (
        (DataClassWithDocstring, "Here is the docstring"),
        (DataClassWithoutDocstring, "DataClassWithoutDocstring(x: int)"),
        (int, None),
    ),
)
def test_docstring_description_plugin(obj, docstring):
    assert build_json_schema(obj).description is None
    assert JSONSchemaBuilder().build(obj).description is None

    assert (
        build_json_schema(
            obj, plugins=[DocstringDescriptionPlugin()]
        ).description
        == docstring
    )
    assert (
        JSONSchemaBuilder(plugins=[DocstringDescriptionPlugin()])
        .build(obj)
        .description
        == docstring
    )


def test_third_party_type_plugin():
    third_party_json_schema = JSONSchema()

    class ThirdPartyTypePlugin(BasePlugin):
        def get_schema(
            self,
            instance: Instance,
            ctx: Context,
            schema: Optional[JSONSchema] = None,
        ) -> Optional[JSONSchema]:
            try:
                if issubclass(instance.type, ThirdPartyType):
                    return third_party_json_schema
            except TypeError:
                pass

    assert (
        build_json_schema(ThirdPartyType, plugins=[ThirdPartyTypePlugin()])
        is third_party_json_schema
    )
    assert (
        JSONSchemaBuilder(plugins=[ThirdPartyTypePlugin()]).build(
            ThirdPartyType
        )
        is third_party_json_schema
    )
    assert (
        JSONSchemaBuilder(plugins=[ThirdPartyTypePlugin()])
        .build(list[ThirdPartyType])
        .items
        is third_party_json_schema
    )
    assert (
        build_json_schema(
            list[ThirdPartyType], plugins=[ThirdPartyTypePlugin()]
        ).items
        is third_party_json_schema
    )
    with pytest.raises(NotImplementedError):
        build_json_schema(ThirdPartyType)
    with pytest.raises(NotImplementedError):
        JSONSchemaBuilder().build(ThirdPartyType)
    with pytest.raises(NotImplementedError):
        build_json_schema(list[ThirdPartyType])
    with pytest.raises(NotImplementedError):
        JSONSchemaBuilder().build(list[ThirdPartyType])
