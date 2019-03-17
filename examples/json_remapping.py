import json
from typing import Dict, Union, Any
from dataclasses import dataclass

from mashumaro import DataClassJSONMixin


Rule = Dict[str, str]
RemappingRules = Dict[str, Union[str, Rule]]


def remapper(d: Dict[str, Any], rules: RemappingRules) -> Dict[str, Any]:
    result = {}
    for key, value in d.items():
        mapped_key = rules.get(key, key)
        if isinstance(mapped_key, tuple):
            value = remapper(value, mapped_key[1])
            result[mapped_key[0]] = value
        else:
            result[mapped_key] = value
    return result


def remap_decoder(data: Union[str, bytes, bytearray],
                  rules: RemappingRules) -> Dict[Any, Any]:
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

    __remapping__ = {
        "ID": "id",
        "USERNAME": "username",
        "EMAIL": "email",
        "COMPANY": ("company", Company.__remapping__),
    }


encoded_data = json.dumps(
    {
        "ID": 1,
        "USERNAME": "user",
        "EMAIL": "example@example.org",
        "COMPANY": {
            "ID": 1,
            "NAME": "company"
        }
    }
)

company = Company(id=1, name="company")
user = User(id=1, username="user", email="example@example.org", company=company)

assert User.from_json(
    data=encoded_data,
    decoder=remap_decoder,
    rules=User.__remapping__) == user
