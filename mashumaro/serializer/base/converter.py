import datetime
from typing import List, Union


def pack_timezone(tz: datetime.timezone):
    # noinspection PyUnresolvedReferences
    init_args = tz.__getinitargs__()
    if len(init_args) == 1:
        return [init_args[0].total_seconds()]
    else:
        return [init_args[0].total_seconds(), init_args[1]]


def unpack_timezone(t: List[Union[float, str]]):
    if len(t) == 1:
        return datetime.timezone(datetime.timedelta(seconds=t[0]))
    else:
        return datetime.timezone(datetime.timedelta(seconds=t[0]), t[1])
