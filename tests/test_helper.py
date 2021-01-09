from mashumaro import field_options


def test_field_options_helper():
    assert field_options() == {"serialize": None, "deserialize": None}

    def serialize(x):
        return x

    def deserialize(x):
        return x

    assert (
        field_options(
            serialize=serialize,
            deserialize=deserialize,
        )
        == {"serialize": serialize, "deserialize": deserialize}
    )
