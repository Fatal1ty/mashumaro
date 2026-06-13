import datetime
import re
from typing import Any

__all__ = ["parse_timezone", "parse_bool", "ConfigValue", "UTC_OFFSET_PATTERN"]


UTC_OFFSET_PATTERN = r"^UTC(([+-][0-2][0-9]):([0-5][0-9]))?$"
UTC_OFFSET_RE = re.compile(UTC_OFFSET_PATTERN)


def parse_timezone(s: str) -> datetime.timezone:
    match = UTC_OFFSET_RE.match(s)
    if not match:
        raise ValueError(
            f"Time zone {s} must be either UTC or in format UTC[+-]hh:mm"
        )
    if match.group(1):
        hours = int(match.group(2))
        minutes = int(match.group(3))
        return datetime.timezone(
            datetime.timedelta(
                hours=hours, minutes=minutes if hours >= 0 else -minutes
            )
        )
    else:
        return datetime.timezone.utc


def parse_bool(value: Any) -> bool:
    # When a bool is used as a mapping key, JSON serialization turns it
    # into the string "true"/"false" (object keys must be strings), so the
    # value coming back from the decoder is that string rather than a real
    # bool. Plain bool(value) would treat both "true" and "false" as True,
    # collapsing the keys, so the strings are mapped back explicitly here.
    if isinstance(value, str):
        if value == "true":
            return True
        if value == "false":
            return False
    return bool(value)


class ConfigValue:
    def __init__(self, name: str):
        self.name = name
