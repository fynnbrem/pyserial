"""The `SerialField`-class.
The main component of this library next to the corresponding `Serializable` in `serializable.py`."""
from dataclasses import Field, MISSING
# noinspection PyUnresolvedReferences
from typing import Union, Optional


class SerialField(Field):
    """A `dataclasses.Field`-subclass that adds extra attributes for serialization:
    :var serialize=True: Whether to serialize this field.
        Note, that by default, even fields with `init=False` will be serialized but (yet) cannot be deserialized.
    :var caster=None:
        A parameter to define an explicit type caster.
        This does not always have to be defined, as in the following cases,
        a proper implicit caster can be derived:
        - The field is annotated with a subclass of `Serializable`. Then the default deserializer of `Serializable`
            will be used.
        - The field is annotated with a primitive type that is callable.
            For example, `tuple` is a primitive type
            and `tuple()` will be used to cast the serialized data into a tuple.
            On the other hand, `tuple[int]` is a complex type and cannot be used as caster.
        - The field is annotated with a subscripted type that only consists of non-union,
            nested iterables and a primitive type at the lowest level.
            For details, see `type_processing.type_to_list()`
    """

    def __init__(
            self, *, serialize=True, caster=None,
            default=MISSING, default_factory=MISSING, init=True, repr=True,
            hash=None, compare=True, metadata=None, kw_only=MISSING, **kwargs
    ):
        # noinspection PyArgumentList
        super().__init__(
            default=default, default_factory=default_factory, init=init, repr=repr,
            hash=hash, compare=compare, metadata=metadata, kw_only=kw_only, **kwargs
        )
        self.serialize = serialize
        self.caster = caster

