import pytest

from mashumaro.meta.macros import PY_37_MIN


@pytest.mark.skipif(not PY_37_MIN, reason="requires python>=3.7")
def test_self_reference():
    from .entities_forward_refs import Node

    assert Node.from_dict({}) == Node()
    assert Node.from_dict({"next": {}}) == Node(Node())
    assert Node().to_dict() == {"next": None}
    assert Node(Node()).to_dict() == {"next": {"next": None}}
