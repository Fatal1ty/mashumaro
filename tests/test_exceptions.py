from dataclasses import dataclass
from typing import List, Union

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder
from mashumaro.core.meta.helpers import type_name
from mashumaro.exceptions import (
    ExtraKeysError,
    InvalidFieldValue,
    MissingDiscriminatorError,
    MissingField,
    SuitableVariantNotFoundError,
    ThirdPartyModuleNotFoundError,
    UnresolvedTypeReferenceError,
    UnserializableField,
    UnsupportedDeserializationEngine,
    UnsupportedSerializationEngine,
)


def test_missing_field_simple_field_type_name():
    exc = MissingField("x", int, object)
    assert exc.field_type_name == "int"


def test_missing_field_generic_field_type_name():
    exc = MissingField("x", List[int], object)
    assert exc.field_type_name == "List[int]"


def test_missing_field_holder_class_name():
    exc = MissingField("x", int, object)
    assert exc.holder_class_name == "object"
    exc = MissingField("x", int, List[int])
    assert exc.holder_class_name == "List[int]"


def test_missing_field_str():
    exc = MissingField("x", int, object)
    assert str(exc) == 'Field "x" of type int is missing in object instance'


def test_unserializable_field_simple_field_type_name():
    exc = UnserializableField("x", int, object)
    assert exc.field_type_name == "int"


def test_unserializable_field_generic_field_type_name():
    exc = UnserializableField("x", List[int], object)
    assert exc.field_type_name == "List[int]"


def test_unserializable_field_holder_class_name():
    exc = UnserializableField("x", int, object)
    assert exc.holder_class_name == "object"
    exc = UnserializableField("x", int, List[int])
    assert exc.holder_class_name == "List[int]"


def test_unserializable_field_str():
    exc = UnserializableField("x", int, object)
    assert str(exc) == 'Field "x" of type int in object is not serializable'


def test_unserializable_field_with_msg_str():
    exc = UnserializableField("x", int, object, "test message")
    assert (
        str(exc) == 'Field "x" of type int in object '
        "is not serializable: test message"
    )


def test_invalid_field_value_simple_field_type_name():
    exc = InvalidFieldValue("x", int, "y", object)
    assert exc.field_type_name == "int"


def test_invalid_field_value_generic_field_type_name():
    exc = InvalidFieldValue("x", List[int], "y", object)
    assert exc.field_type_name == "List[int]"


def test_invalid_field_value_holder_class_name():
    exc = InvalidFieldValue("x", int, "y", object)
    assert exc.holder_class_name == "object"
    exc = InvalidFieldValue("x", int, "y", List[int])
    assert exc.holder_class_name == "List[int]"


def test_invalid_field_value_str():
    exc = InvalidFieldValue("x", int, "y", object)
    assert (
        str(exc) == "Field \"x\" of type int in object has invalid value 'y'"
    )


def test_invalid_field_value_with_msg_str():
    exc = InvalidFieldValue("x", int, "y", object, "test message")
    assert (
        str(exc) == 'Field "x" of type int in object '
        "has invalid value 'y': test message"
    )


def test_third_party_module_not_found_error_holder_class_name():
    exc = ThirdPartyModuleNotFoundError("third_party", "x", object)
    assert exc.holder_class_name == "object"
    exc = ThirdPartyModuleNotFoundError("third_party", "x", List[int])
    assert exc.holder_class_name == "List[int]"


def test_third_party_module_not_found_error_str():
    exc = ThirdPartyModuleNotFoundError("third_party", "x", object)
    assert (
        str(exc) == 'Install "third_party" to use it as the serialization '
        'method for the field "x" in object'
    )


def test_unsupported_deserialization_engine():
    exc = UnsupportedDeserializationEngine("x", int, object, "engine_name")
    assert exc.field_type_name == "int"
    assert exc.holder_class_name == "object"
    assert (
        str(exc) == 'Field "x" of type int in object is not serializable: '
        'Unsupported deserialization engine "engine_name"'
    )


def test_unsupported_serialization_engine():
    exc = UnsupportedSerializationEngine("x", int, object, "engine_name")
    assert exc.field_type_name == "int"
    assert exc.holder_class_name == "object"
    assert (
        str(exc) == 'Field "x" of type int in object is not serializable: '
        'Unsupported serialization engine "engine_name"'
    )


def test_unresolved_type_reference_error():
    exc = UnresolvedTypeReferenceError(object, "x")
    assert exc.holder_class_name == "object"
    assert exc.name == "x"
    assert (
        str(exc) == "Class object has unresolved type reference "
        "x in some of its fields"
    )


def test_missing_discriminator_error():
    exc = MissingDiscriminatorError("x")
    assert exc.field_name == "x"
    assert str(exc) == "Discriminator 'x' is missing"


def test_suitable_variant_not_found_error():
    exc = SuitableVariantNotFoundError(Union[str, int], "type", 42)
    assert exc.discriminator_value == 42
    assert exc.variants_type == Union[str, int]
    assert exc.discriminator_name == "type"
    assert str(exc) == (
        "typing.Union[str, int] has no subtype with attribute 'type' "
        "equal to 42"
    )

    exc = SuitableVariantNotFoundError(Union[str, int], "type")
    assert exc.discriminator_value is None
    assert exc.variants_type == Union[str, int]
    assert exc.discriminator_name == "type"
    assert str(exc) == "typing.Union[str, int] has no suitable subtype"


def test_deserialize_dataclass_from_wrong_value_type():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: str

    with pytest.raises(ValueError) as exc_info:
        MyClass.from_dict(42)
    assert str(exc_info.value) == (
        f"Argument for {type_name(MyClass)}."
        f"__mashumaro_from_dict__ method should be a dict instance"
    )

    decoder = BasicDecoder(MyClass)
    with pytest.raises(ValueError) as exc_info:
        decoder.decode(42)
    assert str(exc_info.value) == (
        f"Argument for {type_name(MyClass)}."
        f"__mashumaro_from_dict__ method should be a dict instance"
    )


def test_extra_keys_error():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: str

        class Config:
            forbid_extra_keys = True

    with pytest.raises(ExtraKeysError) as exc_info:
        MyClass.from_dict({"x": "x", "y": "y"})
    assert str(exc_info.value).endswith(".MyClass: y")
