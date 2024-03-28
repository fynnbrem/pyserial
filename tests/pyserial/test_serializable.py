import datetime
from dataclasses import dataclass
# noinspection PyUnresolvedReferences
from typing import Union, Optional, List, Tuple

from pyserial import SerialField, Serializable

if __name__ == '__main__':
    import json
    from pyserial.conversion.enum_conversion import SerializableEnum

    class E(SerializableEnum):
        x = 1
        y = 2
        z = 3

    @dataclass
    class B(Serializable):
        """This Class is nested in `A`."""
        f: int = SerialField(default=1)


    @dataclass
    class A(Serializable):
        """This Class contains various annotations for fields, some requiring an explicit deserializer."""
        a: str = SerialField()
        b: int = SerialField()
        c: List[int] = SerialField(caster=list)
        d: Tuple[int, ...] = SerialField(caster=tuple)
        e: List[B] = SerialField()
        f: B = SerialField()
        g: Optional[int] = SerialField()
        h: Optional[int] = SerialField()
        i: List[Optional[str]] = SerialField()
        j: E = SerialField()
        k: datetime.datetime = SerialField()

    a_0 = A(
        "1",
        1,
        [1, 2, 3],
        (1, 2, 3),
        [B(1), B(2), B(3)],
        B(),
        None,
        1,
        ["a", None, "c"],
        j=E.x,
        k=datetime.datetime.now()
    )
    d = a_0.serialize()
    print("Before Serialization:\n", a_0)
    print("\n")
    d = json.dumps(d, indent="\t")
    # print("Serialized Data:\n", d)
    # print("\n")
    d = json.loads(d)
    a_1 = A.deserialize(d)
    print("After Serialization:\n", a_1)
    print("\n")
