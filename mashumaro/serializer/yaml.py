import yaml

from mashumaro.serializer.base import DataClassDictMixin


class DataClassYAMLMixin(DataClassDictMixin):
    def to_yaml(self):
        return yaml.dump(self.to_dict())

    @classmethod
    def from_yaml(cls, data: bytes):
        return cls.from_dict(yaml.load(data))
