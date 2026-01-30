type MyTypeAliasType = int | str
from mashumaro.jsonschema import build_json_schema


def test_type_alias_type_with_jsonschema():
    schema = build_json_schema(MyTypeAliasType)
    assert schema.to_dict() == {
        "anyOf": [{"type": "integer"}, {"type": "string"}]
    }
