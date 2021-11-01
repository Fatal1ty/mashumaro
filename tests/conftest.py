from unittest.mock import patch

from mashumaro.meta.macros import PY_37_MIN

if not PY_37_MIN:
    collect_ignore = ["test_pep_563.py"]


fake_add_from_dict = patch(
    "mashumaro.serializer.base.metaprogramming." "CodeBuilder.add_from_dict",
    lambda *args, **kwargs: ...,
)
