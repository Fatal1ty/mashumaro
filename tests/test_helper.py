from mashumaro import field_options
from mashumaro.types import SerializationStrategy


def test_field_options_helper():
    assert field_options() == {
        "serialize": None,
        "deserialize": None,
        "serialization_strategy": None,
    }

    def serialize(x):
        return x  # pragma no cover

    def deserialize(x):
        return x  # pragma no cover

    class TestSerializationStrategy(SerializationStrategy):  # pragma no cover
        def deserialize(self, value):
            return value

        def serialize(self, value):
            return value

    serialization_strategy = TestSerializationStrategy()

    assert field_options(
        serialize=serialize,
        deserialize=deserialize,
        serialization_strategy=serialization_strategy,
    ) == {
        "serialize": serialize,
        "deserialize": deserialize,
        "serialization_strategy": serialization_strategy,
    }
