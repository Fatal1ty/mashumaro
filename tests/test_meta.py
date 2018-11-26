from unittest.mock import patch

import pytest


@patch('sys.version_info', (3, 8))
def test_is_generic_unsupported_python():
    import mashumaro.meta.helpers
    with pytest.raises(NotImplementedError):
        mashumaro.meta.helpers.is_generic(int)
