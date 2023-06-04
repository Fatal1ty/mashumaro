import pytest

from mashumaro.types import Discriminator


def test_discriminator_without_necessary_params():
    with pytest.raises(ValueError) as exc_info:
        Discriminator()
    assert str(exc_info.value) == (
        "Either 'include_supertypes' or 'include_subtypes' must be enabled"
    )

    with pytest.raises(ValueError) as exc_info:
        Discriminator(field="type")
    assert str(exc_info.value) == (
        "Either 'include_supertypes' or 'include_subtypes' must be enabled"
    )
