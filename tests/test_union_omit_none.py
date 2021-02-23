#!/usr/bin/env python
from dataclasses import dataclass
from typing import List, Optional, Union

from mashumaro import DataClassDictMixin
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG


class MyDictMixin(DataClassDictMixin):
    class Config:
        code_generation_options = [
            TO_DICT_ADD_OMIT_NONE_FLAG,
        ]


RawVersion = Union[str, float]


@dataclass
class Package(MyDictMixin):
    pass


@dataclass
class LocalPackage(Package):
    local: str


@dataclass
class GitPackage(Package):
    git: str
    revision: Optional[RawVersion] = None
    warn_unpinned: Optional[bool] = None


PackageSpec = Union[LocalPackage, GitPackage]


@dataclass
class PackageConfig(MyDictMixin):
    packages: List[PackageSpec]


def test_union_with_config():

    pkg_cfg = PackageConfig(
        packages=[
            LocalPackage(local="foo"),
            GitPackage(
                git="git@example.com:fishtown-analytics/dbt-utils.git",
                revision="test-rev",
                warn_unpinned=None,
            ),
        ]
    )

    assert pkg_cfg

    dct = pkg_cfg.to_dict()

    assert dct
