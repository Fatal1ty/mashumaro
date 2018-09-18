import datetime

import msgpack

from mashumaro.serializer.base import DataClassDictMixin


def default_packer(o):
    if isinstance(o, datetime.datetime):
        return o.timestamp()


class DataClassMessagePackMixin(DataClassDictMixin):
    def to_msgpack(self):
        d = self.to_dict(use_bytes=True)
        return msgpack.packb(d, default=default_packer, use_bin_type=True)

    @classmethod
    def from_msgpack(cls, data: bytes):
        return cls.from_dict(msgpack.unpackb(data, raw=False), use_bytes=True)
