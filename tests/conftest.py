from unittest.mock import patch

from mashumaro.core.const import PY_312_MIN

if not PY_312_MIN:
    collect_ignore = [
        "test_generics_pep_695.py",
        "test_pep_695.py",
        "test_recursive_union.py",
        "test_jsonschema/test_jsonschema_pep_695.py",
    ]

add_unpack_method = patch(
    "mashumaro.core.meta.code.builder.CodeBuilder.add_unpack_method",
    lambda *args, **kwargs: ...,
)
