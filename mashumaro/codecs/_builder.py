from types import new_class
from typing import Any, Callable, Dict, Optional, Type

from mashumaro.core.meta.code.builder import CodeBuilder
from mashumaro.core.meta.types.common import FieldContext, ValueSpec
from mashumaro.core.meta.types.pack import PackerRegistry
from mashumaro.core.meta.types.unpack import UnpackerRegistry


class CodecCodeBuilder(CodeBuilder):
    @classmethod
    def new(cls, **kwargs: Any) -> "CodecCodeBuilder":
        return cls(new_class("ns"), **kwargs)

    def get_field_resolved_type_params(
        self, field_name: str
    ) -> Dict[Type, Type]:
        return {}

    def _get_real_type(self, field_name: str, field_type: Type) -> Type:
        return field_type

    def add_decode_method(
        self,
        shape_type: Type,
        decoder_obj: Any,
        pre_decoder_func: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        self.reset()
        with self.indent("def decode(value):"):
            if pre_decoder_func:
                self.ensure_object_imported(pre_decoder_func, "decoder")
                self.add_line("value = decoder(value)")
            unpacked_value = UnpackerRegistry.get(
                ValueSpec(
                    type=shape_type,
                    expression="value",
                    builder=self,
                    field_ctx=FieldContext(name="", metadata={}),
                    could_be_none=False,
                )
            )
            self.add_line(f"return {unpacked_value}")
        self.add_line("setattr(decoder_obj, 'decode', decode)")
        self.ensure_object_imported(decoder_obj, "decoder_obj")
        self.ensure_object_imported(self.cls, "cls")
        self.compile()

    def add_encode_method(
        self,
        shape_type: Type,
        encoder_obj: Any,
        post_encoder_func: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        self.reset()
        with self.indent("def encode(value):"):
            packed_value = PackerRegistry.get(
                ValueSpec(
                    type=shape_type,
                    expression="value",
                    builder=self,
                    field_ctx=FieldContext(name="", metadata={}),
                    could_be_none=False,
                    no_copy_collections=self._get_dialect_or_config_option(
                        "no_copy_collections", ()
                    ),
                )
            )
            if post_encoder_func:
                self.ensure_object_imported(post_encoder_func, "encoder")
                self.add_line(f"return encoder({packed_value})")
            else:
                self.add_line(f"return {packed_value}")
        self.add_line("setattr(encoder_obj, 'encode', encode)")
        self.ensure_object_imported(encoder_obj, "encoder_obj")
        self.ensure_object_imported(self.cls, "cls")
        self.compile()
