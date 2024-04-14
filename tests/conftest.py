from unittest.mock import patch

from mashumaro.core.const import PY_313_MIN

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
