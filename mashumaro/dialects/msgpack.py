from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through


class MessagePackDialect(Dialect):
    serialization_strategy = {
        bytes: pass_through,  # type: ignore
        bytearray: {
            "deserialize": bytearray,
            "serialize": pass_through,
        },
    }


__all__ = ["MessagePackDialect"]
