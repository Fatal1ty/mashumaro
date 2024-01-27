from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional, no_type_check

import pytest

from mashumaro import DataClassDictMixin, field_options, pass_through
from mashumaro.config import ADD_SERIALIZATION_CONTEXT, BaseConfig
from mashumaro.exceptions import BadHookSignature


class BaseClassWithSerializationContext(DataClassDictMixin):
    class Config(BaseConfig):
        code_generation_options = [ADD_SERIALIZATION_CONTEXT]


@dataclass
class Foo(BaseClassWithSerializationContext):
    baz: int

    class Config(BaseConfig):
        code_generation_options = []

    def __pre_serialize__(self):
        return self

    def __post_serialize__(self, d: Dict):
        return d


@dataclass
class Bar(BaseClassWithSerializationContext):
    baz: int

    def __pre_serialize__(self, context: Optional[Dict] = None):
        return self

    def __post_serialize__(self, d: Dict, context: Optional[Dict] = None):
        if context and context.get("omit_baz"):
            d.pop("baz")
        return d


@dataclass
class FooBarBaz(BaseClassWithSerializationContext):
    foo: Foo
    bar: Bar
    baz: int

    def __pre_serialize__(self, context: Optional[Dict] = None):
        return self

    def __post_serialize__(self, d: Dict, context: Optional[Dict] = None):
        if context and context.get("omit_baz"):
            d.pop("baz")
        return d


def test_bad_pre_deserialize_hook():
    with pytest.raises(BadHookSignature):

        class DataClass(DataClassDictMixin):
            x: int

            @no_type_check
            def __pre_deserialize__(
                self, d: Dict[Any, Any]
            ) -> Dict[Any, Any]: ...


def test_bad_post_deserialize_hook():
    with pytest.raises(BadHookSignature):

        class DataClass(DataClassDictMixin):
            x: int

            @no_type_check
            def __post_deserialize__(
                self, obj: "DataClass"
            ) -> "DataClass": ...


def test_pre_deserialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

        @classmethod
        def __pre_deserialize__(cls, d: Dict[Any, Any]) -> Dict[Any, Any]:
            return {k.lower(): v for k, v in d.items()}

    assert DataClass.from_dict({"X": 123}) == DataClass(x=123)


def test_post_deserialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

        @classmethod
        def __post_deserialize__(cls, obj: "DataClass") -> "DataClass":
            obj.x = 456
            return obj

    assert DataClass.from_dict({"x": 123}) == DataClass(x=456)


def test_pre_serialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        counter: ClassVar[int] = 0

        def __pre_serialize__(self) -> "DataClass":
            DataClass.counter += 1
            return self

    instance = DataClass(x=123)
    assert instance.to_dict() == {"x": 123}
    assert instance.counter == 1


def test_post_serialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        counter: ClassVar[int] = 0

        def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
            return {k.upper(): v for k, v in d.items()}

    instance = DataClass(x=123)
    assert instance.to_dict() == {"X": 123}


def test_hook_stub_is_not_called(mocker):
    pre_deserialize_hook = mocker.patch.object(
        DataClassDictMixin, "__pre_deserialize__"
    )
    post_deserialize_hook = mocker.patch.object(
        DataClassDictMixin, "__post_deserialize__"
    )
    pre_serialize_hook = mocker.patch.object(
        DataClassDictMixin, "__pre_serialize__"
    )
    post_serialize_hook = mocker.patch.object(
        DataClassDictMixin, "__post_serialize__"
    )

    @dataclass
    class A(DataClassDictMixin):
        a: int

    obj = A.from_dict({"a": 1})
    obj.to_dict()

    pre_deserialize_hook.assert_not_called()
    post_deserialize_hook.assert_not_called()
    pre_serialize_hook.assert_not_called()
    post_serialize_hook.assert_not_called()


def test_hook_in_parent_class(mocker):
    class A:
        @classmethod
        def __pre_deserialize__(cls, d):
            return d  # pragma: no cover

        @classmethod
        def __post_deserialize__(cls, obj):
            return obj  # pragma: no cover

        def __pre_serialize__(self):
            return self  # pragma: no cover

        def __post_serialize__(self, d):
            return d  # pragma: no cover

    @dataclass
    class B(A, DataClassDictMixin):
        a: int

    pre_deserialize_hook = mocker.patch.object(A, "__pre_deserialize__")
    post_deserialize_hook = mocker.patch.object(A, "__post_deserialize__")
    pre_serialize_hook = mocker.patch.object(
        A, "__pre_serialize__", return_value=B(a=1)
    )
    post_serialize_hook = mocker.patch.object(A, "__post_serialize__")

    B.from_dict({"a": 1})
    B(a=1).to_dict()

    pre_deserialize_hook.assert_called_once()
    post_deserialize_hook.assert_called_once()
    pre_serialize_hook.assert_called_once()
    post_serialize_hook.assert_called_once()


def test_post_deserialize_hook_with_pass_through_field():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: int = field(metadata=field_options(deserialize=pass_through))

        @classmethod
        def __post_deserialize__(cls, obj):
            return obj

    assert MyClass.from_dict({"x": 42}) == MyClass(42)


def test_post_deserialize_hook_with_empty_dataclass():
    @dataclass
    class MyClass(DataClassDictMixin):
        @classmethod
        def __post_deserialize__(cls, obj):
            return obj  # pragma: no cover

    assert MyClass.from_dict({}) == MyClass()


def test_passing_context_into_hook():
    foo = FooBarBaz(foo=Foo(1), bar=Bar(baz=2), baz=3)
    assert foo.to_dict() == {"foo": {"baz": 1}, "bar": {"baz": 2}, "baz": 3}
    assert foo.to_dict(context={"omit_baz": True}) == {
        "foo": {"baz": 1},
        "bar": {},
    }
