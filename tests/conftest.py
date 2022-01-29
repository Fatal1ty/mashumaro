from unittest.mock import patch

from mashumaro.core.const import PY_37_MIN

if not PY_37_MIN:
    collect_ignore = ["test_pep_563.py"]


fake_add_from_dict = patch(
    "mashumaro.core.metaprogramming." "CodeBuilder.add_from_dict",
    lambda *args, **kwargs: ...,
)
