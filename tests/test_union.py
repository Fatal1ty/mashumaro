import pytest

from .entities import ShapeCollection, CustomShape

from mashumaro.exceptions import InvalidFieldValue


def test_union():
    dumped = {"shapes": ["triange", {"name": "square", "num_corners": 4}]}
    assert ShapeCollection.from_dict(dumped).to_dict() == dumped


def test_invalid_union():
    dumped = {"shapes": ["triange", {"badfield": True}]}
    with pytest.raises(InvalidFieldValue):
        ShapeCollection.from_dict(dumped)


def test_invalid_union_no_match_from_dict():
    dumped = {"shapes": ["triange", {"name": "square", "num_corners": "four"}]}
    with pytest.raises(ValueError):
        ShapeCollection.from_dict(dumped)


def test_invalid_union_no_match_to_dict():
    invalid = ShapeCollection(
        shapes=[
            "triange",
            CustomShape(name="square", num_corners="four"),
        ]
    )

    with pytest.raises(ValueError):
        invalid.to_dict()
