from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

import pytest
from typing_extensions import Annotated, Literal

from mashumaro import field_options
from mashumaro.config import TO_DICT_ADD_BY_ALIAS_FLAG, BaseConfig
from mashumaro.exceptions import ExtraKeysError, MissingDiscriminatorError
from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.types import Alias, Discriminator


class Profession(str, Enum):
    UNKNOWN = "unknown"
    DENTIST = "dentist"
    SURGEON = "surgeon"


class BaseModel(DataClassDictMixin):
    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]
        allow_deserialization_not_by_alias = True


@dataclass
class Address(BaseModel):
    street: str = field(metadata=field_options(alias="s"))
    zip_code: str = field(metadata=field_options(alias="z"))


@dataclass
class Person(BaseModel):
    first_name: str = field(metadata=field_options(alias="fn"))
    last_name: str = field(metadata=field_options(alias="ln"))
    address: Optional[Address] = field(
        metadata=field_options(alias="a"), default=None
    )
    profession: Profession = field(
        metadata=field_options(alias="p"), default=Profession.UNKNOWN
    )

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]
        discriminator = Discriminator(
            field="profession", include_subtypes=True
        )
        allow_deserialization_not_by_alias = True


@dataclass
class Dentist(Person):
    profession: Profession = field(
        metadata=field_options(alias="p"), default=Profession.DENTIST
    )


@dataclass
class Surgeon(Person):
    profession: Profession = field(
        metadata=field_options(alias="p"), default=Profession.SURGEON
    )


def test_model_load():
    raw_data = {
        "first_name": "jerry",
        "last_name": "seefree",
        "address": {"street": "15256 green st", "zip_code": "16563"},
        "profession": "surgeon",
    }

    m = Person.from_dict(raw_data)
    assert m.first_name == "jerry"
    assert isinstance(m, Surgeon)


def test_model_load_alias():
    raw_data = {
        "fn": "jerry",
        "ln": "seefree",
        "a": {"s": "15256 green st", "z": "16563"},
        "p": "surgeon",
    }

    p = Person.from_dict(raw_data)
    assert isinstance(p, Surgeon)


def test_model_load_missing_discriminator():
    with pytest.raises(MissingDiscriminatorError) as exc_info:
        Person.from_dict({"fn": "jerry", "ln": "seefree"})
    assert exc_info.value.field_name == "profession"


def test_class_discriminator_payload_alias():
    # Discriminator.field stays the Python attribute used to register
    # variants; aliases only affect which payload keys are read.
    @dataclass
    class Animal(DataClassDictMixin):
        name: str = field(metadata=field_options(alias="n"))
        kind: str = field(metadata=field_options(alias="k"), default="animal")

        class Config(BaseConfig):
            discriminator = Discriminator(field="kind", include_subtypes=True)
            allow_deserialization_not_by_alias = True

    @dataclass
    class Cat(Animal):
        kind: str = field(metadata=field_options(alias="k"), default="cat")

    assert isinstance(Animal.from_dict({"name": "x", "kind": "cat"}), Cat)
    assert isinstance(Animal.from_dict({"n": "x", "k": "cat"}), Cat)


def test_discriminator_alias_annotation():
    @dataclass
    class Node(DataClassDictMixin):
        kind: Annotated[str, Alias("t")] = "node"

        class Config(BaseConfig):
            discriminator = Discriminator(field="kind", include_subtypes=True)
            allow_deserialization_not_by_alias = True

    @dataclass
    class Leaf(Node):
        kind: Annotated[str, Alias("t")] = "leaf"

    assert isinstance(Node.from_dict({"kind": "leaf"}), Leaf)
    assert isinstance(Node.from_dict({"t": "leaf"}), Leaf)


def test_discriminator_config_aliases():
    @dataclass
    class Node(DataClassDictMixin):
        kind: str = "node"

        class Config(BaseConfig):
            aliases = {"kind": "t"}
            discriminator = Discriminator(field="kind", include_subtypes=True)
            allow_deserialization_not_by_alias = True

    @dataclass
    class Leaf(Node):
        kind: str = "leaf"

    assert isinstance(Node.from_dict({"kind": "leaf"}), Leaf)
    assert isinstance(Node.from_dict({"t": "leaf"}), Leaf)


def test_discriminator_multiple_aliases():
    @dataclass
    class Node(DataClassDictMixin):
        kind: str = field(metadata=field_options(alias=["t", "type"]))

        class Config(BaseConfig):
            discriminator = Discriminator(field="kind", include_subtypes=True)
            allow_deserialization_not_by_alias = True

    @dataclass
    class Leaf(Node):
        kind: str = field(
            default="leaf", metadata=field_options(alias=["t", "type"])
        )

    assert isinstance(Node.from_dict({"kind": "leaf"}), Leaf)
    assert isinstance(Node.from_dict({"t": "leaf"}), Leaf)
    assert isinstance(Node.from_dict({"type": "leaf"}), Leaf)


def test_annotated_union_discriminator_with_alias():
    @dataclass
    class Email:
        channel: Literal["email"] = field(
            default="email", metadata=field_options(alias="ch")
        )
        address: str = ""

    @dataclass
    class SMS:
        channel: Literal["sms"] = field(
            default="sms", metadata=field_options(alias="ch")
        )
        number: str = ""

    Notification = Annotated[
        Union[Email, SMS],
        Discriminator(field="channel", include_supertypes=True),
    ]

    @dataclass
    class Job(DataClassDictMixin):
        notification: Notification

        class Config(BaseConfig):
            allow_deserialization_not_by_alias = True

    job = Job.from_dict({"notification": {"ch": "sms", "number": "+1"}})
    assert isinstance(job.notification, SMS)
    job = Job.from_dict(
        {"notification": {"channel": "email", "address": "a@b.c"}}
    )
    assert isinstance(job.notification, Email)


def test_forbid_extra_keys_allows_discriminator_alias():
    @dataclass
    class Node(DataClassDictMixin):
        kind: str = field(metadata=field_options(alias="t"), default="node")

        class Config(BaseConfig):
            discriminator = Discriminator(field="kind", include_subtypes=True)
            allow_deserialization_not_by_alias = True
            forbid_extra_keys = True

    @dataclass
    class Leaf(Node):
        kind: str = field(metadata=field_options(alias="t"), default="leaf")

    assert isinstance(Node.from_dict({"t": "leaf"}), Leaf)
    with pytest.raises(ExtraKeysError):
        Node.from_dict({"t": "leaf", "nope": 1})
