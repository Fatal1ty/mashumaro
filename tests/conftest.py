from unittest.mock import patch

add_unpack_method = patch(
    "mashumaro.core.meta.code.builder.CodeBuilder.add_unpack_method",
    lambda *args, **kwargs: ...,
)
