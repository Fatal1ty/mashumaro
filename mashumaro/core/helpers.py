import datetime
import re

__all__ = [
    "parse_timezone",
    "ConfigValue",
]


def parse_timezone(s: str) -> datetime.timezone:
    regexp = re.compile(r"^UTC(([+-][0-2][0-9]):([0-5][0-9]))?$")
    match = regexp.match(s)
    if not match:
        raise ValueError(
            f"Time zone {s} must be either UTC " f"or in format UTC[+-]hh:mm"
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


class ConfigValue:
    def __init__(self, name: str):
        self.name = name
