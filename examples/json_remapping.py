import json
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from mashumaro import DataClassJSONMixin

Rule = Dict[str, str]
RemappingRules = Dict[str, Union[str, Rule]]


def object_remapper(
    d: Dict[str, Any], rules: RemappingRules
) -> Dict[str, Any]:
    result = {}
    for key, value in d.items():
        mapped_key = rules.get(key, key)
        if isinstance(mapped_key, tuple):
            value = remapper(value, mapped_key[1])
            result[mapped_key[0]] = value
        else:
            result[mapped_key] = value
    return result


def remapper(data, rules):
    if isinstance(data, dict):
        return object_remapper(data, rules)
    elif isinstance(data, list):
        return [object_remapper(d, rules) for d in data]


def remap_decoder(
    data: Union[str, bytes, bytearray], rules: RemappingRules
) -> Dict[Any, Any]:
    d = json.loads(data)
    return remapper(d, rules)


@dataclass
class Company(DataClassJSONMixin):
    id: int
    name: str

    __remapping__ = {
        "ID": "id",
        "NAME": "name",
    }


@dataclass
class User(DataClassJSONMixin):
    id: int
    username: str
    email: str
    company: Company
    contractors: List[Company]

    __remapping__ = {
        "ID": "id",
        "USERNAME": "username",
        "EMAIL": "email",
        "COMPANY": ("company", Company.__remapping__),
        "CONTRACTORS": ("contractors", Company.__remapping__),
    }


encoded_data = json.dumps(
    {
        "ID": 1,
        "USERNAME": "user",
        "EMAIL": "example@example.org",
        "COMPANY": {"ID": 1, "NAME": "company1"},
        "CONTRACTORS": [{"ID": 2, "NAME": "company2"}],
    }
)

user = User(
    id=1,
    username="user",
    email="example@example.org",
    company=Company(id=1, name="company1"),
    contractors=[Company(id=2, name="company2")],
)

assert (
    User.from_json(
        data=encoded_data, decoder=remap_decoder, rules=User.__remapping__
    )
    == user
)
