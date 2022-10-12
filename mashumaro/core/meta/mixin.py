from mashumaro.core.meta.builder import CodeBuilder


def compile_mixin_unpacker(cls, format_name, dialect, decoder):
    builder = CodeBuilder(
        cls=cls,
        format_name=format_name,
        decoder=decoder,
        default_dialect=dialect,
    )
    builder.add_unpack_method()


def compile_mixin_packer(self, format_name, dialect, encoder):
    builder = CodeBuilder(
        cls=self.__class__,
        format_name=format_name,
        encoder=encoder,
        default_dialect=dialect,
    )
    builder.add_pack_method()


__all__ = ["compile_mixin_unpacker", "compile_mixin_packer"]
