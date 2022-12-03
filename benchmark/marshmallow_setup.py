from marshmallow import Schema, fields

from benchmark.enums import *


class MARSHMALLOWSimpleClass(Schema):
    int = fields.Int()
    float = fields.Float()
    str = fields.Str()
    bool = fields.Bool()


class MARSHMALLOWEnumClass(Schema):
    enum = fields.Enum(MyEnum, by_value=True)
    str_enum = fields.Enum(MyStrEnum, by_value=True)
    int_enum = fields.Enum(MyIntEnum, by_value=True)
    flag = fields.Enum(MyFlag, by_value=True)
    int_flag = fields.Enum(MyIntFlag, by_value=True)


class MARSHMALLOWDateTimeClass(Schema):
    datetime = fields.DateTime()
    date = fields.Date()
    time = fields.Time()
    timedelta = fields.TimeDelta()


class MARSHMALLOWClass(Schema):
    list_simple = fields.List(fields.Nested(MARSHMALLOWSimpleClass()))
    list_enum = fields.List(fields.Nested(MARSHMALLOWEnumClass()))
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
