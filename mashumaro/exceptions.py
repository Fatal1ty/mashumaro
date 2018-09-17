class MissingField(Exception):
    def __init__(self, field_name, field_type, holder_class):
        self.field_name = field_name
        self.field_type = field_type
        self.holder_class = holder_class

    @property
    def field_type_name(self):
        try:
            return f"{self.field_type.__module__}.{self.field_type.__name__}"
        except AttributeError:
            return str(self.field_type)

    @property
    def holder_class_name(self):
        return self.holder_class.__name__
        # return f"{self.holder_class.__module__}." \
        #        f"{self.holder_class.__name__}"

    def __str__(self):
        return f'Field "{self.field_name}" of type {self.field_type_name}' \
               f' is missing in {self.holder_class} instance'


class UnserializableDataError(Exception):
    pass


class UnserializableField(UnserializableDataError):
    def __init__(self, field_name, field_type, holder_class):
        self.field_name = field_name
        self.field_type = field_type
        self.holder_class = holder_class

    @property
    def field_type_name(self):
        try:
            return f"{self.field_type.__module__}.{self.field_type.__name__}"
        except AttributeError:
            return str(self.field_type)

    @property
    def holder_class_name(self):
        return self.holder_class.__name__
        # return f"{self.holder_class.__module__}." \
        #        f"{self.holder_class.__name__}"

    def __str__(self):
        return f'Field "{self.field_name}" of type {self.field_type_name} ' \
               f'in {self.holder_class} is not serializable'
