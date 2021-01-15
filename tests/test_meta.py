from dataclasses import dataclass
from unittest.mock import patch

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.meta.helpers import (
    get_class_that_define_method,
    is_class_var,
    is_generic,
    is_init_var,
)
from mashumaro.serializer.base.metaprogramming import CodeBuilder


def test_is_generic_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
                    with pytest.raises(NotImplementedError):
                        is_generic(int)


def test_is_class_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
                    with pytest.raises(NotImplementedError):
                        is_class_var(int)


def test_is_init_var_unsupported_python():
    with patch("mashumaro.meta.helpers.PY_36", False):
        with patch("mashumaro.meta.helpers.PY_37", False):
            with patch("mashumaro.meta.helpers.PY_38", False):
                with patch("mashumaro.meta.helpers.PY_39", False):
                    with pytest.raises(NotImplementedError):
                        is_init_var(int)


def test_no_code_builder():
    with patch(
        "mashumaro.serializer.base.dict."
        "DataClassDictMixin.__init_subclass__",
        lambda: ...,
    ):

        @dataclass
        class DataClass(DataClassDictMixin):
            pass

        assert DataClass.from_dict({}) is None
        assert DataClass().to_dict() is None
        assert DataClass.__pre_deserialize__({}) is None
        assert DataClass.__post_deserialize__(DataClass()) is None
        assert DataClass().__pre_serialize__() is None
        assert DataClass().__post_serialize__({}) is None


def test_get_class_that_define_method():
    class A:
        def foo(self):
            pass  # pragma no cover

        @classmethod
        def bar(cls):
            pass  # pragma no cover

        def foobar(self):
            pass  # pragma no cover

    class B(A):
        def foobar(self):
            pass  # pragma no cover

    assert get_class_that_define_method("foo", B) == A
    assert get_class_that_define_method("bar", B) == A
    assert get_class_that_define_method("foobar", B) == B


def test_get_unknown_declared_hook():
    builder = CodeBuilder(object)
    assert builder.get_declared_hook("unknown_name") is None
