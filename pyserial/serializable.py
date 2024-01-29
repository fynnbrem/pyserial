import json
from dataclasses import dataclass, fields
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional, TypeVar, Callable, Any, Iterable

from pyserial.serialization import SerialDict, serialize, serializer_func
from serial_field import SerialField




@dataclass
class Serializable:
    def serialize(self) -> SerialDict:
        data = dict()
        for field in fields(self):
            attr = self.__getattribute__(field.name)
            data[field.name] = serialize(attr)
        return data

    @classmethod
    def deserialize(cls, data: SerialDict):
        deserialized_data = dict()
        for field_ in fields(cls):
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
    return serializable.serialize()
@dataclass
class B(Serializable):
    f: int = SerialField(default=1)


@dataclass
class A(Serializable):
    a: str = SerialField()
    b: int = SerialField()
    c: list[int] = SerialField(deserializer=list)
    d: tuple[int, ...] = SerialField(deserializer=tuple)
    e: B = SerialField(default_factory=B)
    f: Path = SerialField(default=Path("C:/"))


a_0 = A("1", 1, [1, 2, 3], (1, 2, 3))
d = a_0.serialize()
print(a_0)
d = json.dumps(d)
print(d)
d = json.loads(d)
a_1 = A.deserialize(d)
print(a_1)
