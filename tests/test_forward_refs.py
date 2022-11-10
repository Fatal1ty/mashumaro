from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mashumaro import DataClassDictMixin


@dataclass
class Node(DataClassDictMixin):
    next: Optional[Node] = None


def test_self_reference():
    assert Node.from_dict({}) == Node()
    assert Node.from_dict({"next": {}}) == Node(Node())
    assert Node().to_dict() == {"next": None}
    assert Node(Node()).to_dict() == {"next": {"next": None}}
