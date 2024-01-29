"""The `Serializable`-class.
The main component of this library next to the corresponding `SerialField` in `serial_field.py`."""

from dataclasses import dataclass, fields
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional, TypeVar, Callable, Any, Iterable, Type

from pyserial.serialization import SerialDict, serialize, serializer_func, SerialTypes
from pyserial.serial_field import SerialField


@dataclass
class Serializable:
    """
    Mixin to add default serialization behaviour.

    Introduction
    ============
    This class allows seamless conversion between the limited types of a serial format and the broader types of Python.
    For example, an attribute of the type `Path` will automatically get saved as `str`,
    but will then be deserialized as `Path` again.

    Usage
    =====
    Requires the class to be decorated as dataclass
    and all fields to be serialized must be initialized as `SerialField`
    (in contrast to the standard-`dataclasses.field`).

    Details
    =======
    Using `.serialize()`/`.deserialize()`, only the corresponding fields will be serialized and upon deserialization
    will be cast back into their proper type.
    Also handles missing or extra fields, see `.deserialize()` for details.
    """

    def serialize(self) -> SerialDict:
        """Converts this class with alls its fields class
        that are a `SerialField` and have `serialize=True` into a `SerialDict`"""
        data = dict()
        for field_ in fields(self):
            if not isinstance(field_, SerialField) or not field_.serialize:
                continue
            field_: SerialField
            attr = self.__getattribute__(field_.name)
            data[field_.name] = serialize(attr)
        return data

    @classmethod
    def deserialize(cls, data: SerialDict):
        """Loads this class from a `SerialDict`.
        All fields will be deserialized with their current deserializer.
        The deserializer they had during serialization has no effect on this.

        .. DANGER::
        This process will *not* force the attributes onto an empty class but will
        actually call the constructor of the class with the deserialized values as arguments.

        Changes in the signature of the class between serializations is handled in the following way:
        - Deserialized fields that are missing in the constructor will be completely skipped.
        - Fields that are in the constructor but not in the deserialized data are required to
         have a default value defined.
        """
        deserialized_data = dict()
        for field_ in fields(cls):
            if not isinstance(field_, SerialField):
                continue
            field_: SerialField

            if field_.deserializer is not None:
                deserializer = field_.deserializer
            elif issubclass(field_.type, Serializable):
                deserializer = field_.type.deserialize
            elif isinstance(field_.type, type):
                deserializer = field_.type
            else:
                raise ValueError(
                    "Tried to deserialize a field which has no flat type or deserializer defined.\n"
                    "Define a deserializer for the field when using complex types."
                )

            deserialized_data[field_.name] = deserializer(data[field_.name])
        return cls(**deserialized_data)


@serializer_func(Serializable)
def run(serializable: Serializable) -> SerialDict:
    """`Serializable` must be serialized with their own `.serialize()`"""
    return serializable.serialize()


def nested_deserializer(iterable_type: Type[Union[list, tuple]], item_deserializer: Callable) -> Callable:
    """Creates a deserializer that will deserialize
    an iterable and then also all its items with the `item_deserializer`."""

    def inner(items: list) -> iterable_type:
        new_items = [item_deserializer(i) for i in items]
        return iterable_type(new_items)

    return inner


if __name__ == '__main__':
    import json


    @dataclass
    class B(Serializable):
        """This Class is nested in `A`."""
        f: int = SerialField(default=1)


    @dataclass
    class A(Serializable):
        """This Class contains various annotations for fields, some requiring an explicit deserializer."""
        a: str = SerialField()
        b: int = SerialField()
        c: list[int] = SerialField(deserializer=list)
        d: tuple[int, ...] = SerialField(deserializer=tuple)
        e: list[B] = SerialField(deserializer=nested_deserializer(list, B.deserialize))
        f: B = SerialField(default_factory=B)


    a_0 = A("1", 1, [1, 2, 3], (1, 2, 3), [B(1), B(2), B(3)])
    d = a_0.serialize()
    print(a_0)
    d = json.dumps(d, indent="\t")
    print(d)
    d = json.loads(d)
    a_1 = A.deserialize(d)
    print(a_1)
