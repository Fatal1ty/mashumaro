from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from typing_extensions import Self

from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.models import JSONArraySchema, JSONObjectSchema


def test_jsonschema_supports_self_with_refs() -> None:
    @dataclass
    class Node:
        child: Optional[Self] = None
        items: list[Self] = None  # type: ignore[assignment]

    schema = build_json_schema(Node, all_refs=True)

    # Top-level schema should be a $ref into $defs
    assert schema.reference is not None
    assert schema.reference.startswith("#/$defs/")

    def_key = schema.reference.split("#/$defs/", 1)[1]

    # And the referenced definition should exist in $defs
    assert schema.definitions is not None
    assert def_key in schema.definitions

    node_def = schema.definitions[def_key]
    assert isinstance(node_def, JSONObjectSchema)

    # Optional[Self] => anyOf [$ref-to-self, null]
    child_schema = node_def.properties["child"]
    assert child_schema.anyOf is not None
    assert any(s.reference == schema.reference for s in child_schema.anyOf)
    assert any(
        getattr(s.type, "value", None) == "null" for s in child_schema.anyOf
    )

    # list[Self] => array items $ref-to-self
    items_schema = node_def.properties["items"]
    assert isinstance(items_schema, JSONArraySchema)
    assert items_schema.items is not None
    assert items_schema.items.reference == schema.reference


def test_jsonschema_self_forces_refs_when_recursive_even_without_all_refs() -> (
    None
):
    @dataclass
    class Node:
        child: Self | None = None

    schema = build_json_schema(Node)

    # For recursive dataclasses we expect $defs/$ref even if all_refs=False
    assert schema.reference == "#/$defs/Node"
    assert schema.definitions is not None
    assert "Node" in schema.definitions

    node_def = schema.definitions["Node"].to_dict()
    assert node_def.get("title") == "Node"
    assert node_def.get("type") == "object"
    assert node_def.get("properties", {}).get("child", {}).get("anyOf")
