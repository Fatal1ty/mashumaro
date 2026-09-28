import traceback
from dataclasses import dataclass

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.core.meta.code.builder import CodeBuilder
from mashumaro.dialect import Dialect
from mashumaro.exceptions import InvalidFieldValue


class EmptyDialect(Dialect):
    pass


@dataclass
class Inner(DataClassDictMixin):
    x: int


@dataclass
class Outer(DataClassDictMixin):
    inner: Inner


def _expected_filename(cls: type) -> str:
    return f"<mashumaro {cls.__module__}.{cls.__name__}>"


def test_generated_method_code_filename():
    for cls in (Inner, Outer):
        for method_name in (
            "__mashumaro_from_dict__",
            "__mashumaro_to_dict__",
        ):
            code = getattr(cls, method_name).__code__
            assert code.co_filename == _expected_filename(cls)


def test_generated_code_filename_with_dialect():
    builder = CodeBuilder(cls=Inner, dialect=EmptyDialect)
    assert builder.generated_code_filename == (
        f"<mashumaro {Inner.__module__}.{Inner.__name__}"
        f"[{EmptyDialect.__module__}.{EmptyDialect.__name__}]>"
    )


def test_generated_code_frames_have_identifiable_filenames():
    with pytest.raises(InvalidFieldValue) as exc_info:
        Outer.from_dict({"inner": {"x": "not-an-int"}})

    expected = {_expected_filename(Inner), _expected_filename(Outer)}
    generated_frames = []
    exc: BaseException = exc_info.value
    while exc is not None:
        for frame in traceback.extract_tb(exc.__traceback__):
            if frame.name.startswith("__mashumaro_"):
                generated_frames.append(frame)
        exc = exc.__cause__ or exc.__context__

    assert generated_frames
    for frame in generated_frames:
        assert frame.filename in expected
