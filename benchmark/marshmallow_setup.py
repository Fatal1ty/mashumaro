from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from benchmark.enums import *


class MARSHMALLOWSimpleClass(Schema):
    int = fields.Int()
    float = fields.Float()
    str = fields.Str()
    bool = fields.Bool()


class MARSHMALLOWEnumClass(Schema):
    enum = EnumField(MyEnum)
    str_enum = EnumField(MyStrEnum)
    int_enum = EnumField(MyIntEnum)
    flag = EnumField(MyFlag)
    int_flag = EnumField(MyIntFlag)


class MARSHMALLOWDateTimeClass(Schema):
    datetime = fields.DateTime()
    date = fields.Date()
    time = fields.Time()
    timedelta = fields.TimeDelta()


class MARSHMALLOWClass(Schema):
    list_simple = fields.List(fields.Nested(MARSHMALLOWSimpleClass()))
    # list_enum = fields.List(fields.Nested(MARSHMALLOWEnumClass()))
    tuple_datetime = fields.List(fields.Nested(MARSHMALLOWDateTimeClass()))
    dict_complex = fields.Dict(
        keys=fields.Int(),
        values=fields.Mapping(
            keys=fields.Str(),
            values=fields.Mapping(
                keys=fields.UUID(), values=fields.List(fields.Decimal())
            ),
        ),
    )
