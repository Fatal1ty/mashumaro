import msgpack

from mashumaro.serializer.base import DataClassDictMixin


class DataClassMessagePackMixin(DataClassDictMixin):
    def to_msgpack(self):
        d = self.to_dict(use_bytes=True)
        return msgpack.packb(d, use_bin_type=True)

    @classmethod
    def from_msgpack(cls, data: bytes):
        return cls.from_dict(msgpack.unpackb(data, raw=False), use_bytes=True)
