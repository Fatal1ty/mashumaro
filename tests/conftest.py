from unittest.mock import patch

from mashumaro.core.const import PY_312_MIN, PY_313_MIN

if not PY_312_MIN:
    collect_ignore = [
        "test_generics_pep_695.py",
        "test_pep_695.py",
        "test_recursive_union.py",
    ]

if PY_313_MIN:
    collect_ignore = [
        "test_codecs/test_orjson_codec.py",
        "test_discriminated_unions/test_dialects.py",
        "test_orjson.py",
        "test_pep_563.py",
        "test_self.py",
    ]

add_unpack_method = patch(
    "mashumaro.core.meta.code.builder.CodeBuilder.add_unpack_method",
    lambda *args, **kwargs: ...,
)
