from unittest.mock import patch
from dataclasses import dataclass

import pytest

from mashumaro.meta.helpers import is_generic
from mashumaro import DataClassDictMixin


def test_is_generic_unsupported_python():
    with patch('mashumaro.meta.helpers.PY_36', False):
        with patch('mashumaro.meta.helpers.PY_37', False):
            with pytest.raises(NotImplementedError):
                is_generic(int)


def test_no_code_builder():
    class Mock:
        def add_from_dict(self):
            pass

        def add_to_dict(self):
            pass
    with patch('mashumaro.serializer.base.metaprogramming.CodeBuilder', Mock):
        @dataclass
        class DataClass(DataClassDictMixin):
            pass
        assert DataClass.from_dict({}) is None
        assert DataClass().to_dict() is None
