from unittest.mock import patch

import pytest

from mashumaro.meta.helpers import is_generic


def test_is_generic_unsupported_python():
    with patch('mashumaro.meta.helpers.PY_36', False):
        with patch('mashumaro.meta.helpers.PY_37', False):
            with pytest.raises(NotImplementedError):
                is_generic(int)
