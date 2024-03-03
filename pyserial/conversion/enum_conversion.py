from enum import Enum
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Type, TypeVar, Any

from pyserial.conversion.serialization import serializer_func

T = TypeVar("T")


class SerializableEnum(Enum):
    """An Enum which additionally provides support for serialization of the members.
    By default, it will be serialized by value.
    You can override `serialize()` and `deserialize()` to change this behaviour.

    Note that using the value is also the fallback behaviour for `Enum`s not stemming from this class.
    So if you are using the default behaviour, you can also use the default `Enum` for the same effect.

    Also look into `SerializableEnumByName` for a preset if you want to serialize by name."""

    def serialize(self: Enum) -> Union[str, int]:
        """The value to serialize the member by. Default is `.value`."""
        return self.value

    @classmethod
    def deserialize(cls: Type[T], value: Any) -> T:
        """The method to cast a `value` into a member. Default is value-to-member."""
        return cls(value)


class SerializableEnumByName(SerializableEnum):
    """An Enum which additionally provides support for serialization of the members.
    It will be serialized by name."""

    def serialize(self: Enum) -> str:
        """The name of this member."""
        return self.name

    @classmethod
    def deserialize(cls: Type[T], value: str) -> T:
        """Returns the member of this Enum based on the `.name` corresponding to the `value`."""
        return cls[value]


@serializer_func(SerializableEnum)
def run(enum: SerializableEnum) -> Union[str, int]:
    """Enums will be cast into their value."""
    return enum.serialize()
