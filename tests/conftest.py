from unittest.mock import patch

from mashumaro.core.const import PY_37_MIN

if not PY_37_MIN:
    collect_ignore = ["test_pep_563.py", "test_toml.py"]


add_unpack_method = patch(
    "mashumaro.core.meta.builder.CodeBuilder.add_unpack_method",
    lambda *args, **kwargs: ...,
)
