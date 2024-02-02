from itertools import permutations
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Any, Type

from pyserial.serialization import add_serializer, _SERIALIZERS, get_serializer, serialize


class A():
    ...


class AB(A):
    ...


class ABC(AB):
    ...


def test_manage_serializer():
    """Blackbox test of `get_serializer()` and `add_serializer()`.
    Adds three classes, that are subclasses of one another to the serializers and when getting the serializer,
     expects to get the serializer for that exact class and not its superclass,
     independent of the order the classes were added to the serializers.
    """
    classes = [A, AB, ABC]
    classes: list[tuple[int, Type[A]]] = list(enumerate(classes))

    def test(sequence):
        _SERIALIZERS.clear()
        for type_, serializer in sequence:
            add_serializer(type_, serializer)

        for want_index, class_ in classes:
            got_index = get_serializer(class_)()
            assert got_index == want_index, \
                f"{got_index =}, {want_index =}, sequence = {[str(inst) for inst, idx in sequence]}"

    serializers = [(inst, lambda i_=idx: i_) for idx, inst in classes]
    # ↑ The indexes are used as sentinel values to identify the proper serializer
    perms = permutations(serializers)
    for perm in perms:
        test(perm)


def test_get_serializer_superclass():
    """Tries to get the serializer for a subclass for which no serializer exists yet, but for its superclass."""

    def test(superclass, subclass):
        _SERIALIZERS.clear()
        add_serializer(superclass, lambda: 1)  # 1 As sentinel value for the proper serializer
        assert get_serializer(subclass)() == 1, f"{subclass =}, {superclass =}"

    test(A, AB)
    test(A, ABC)
    test(AB, ABC)


def test_get_serializer_no_exist():
    """Tries to get the serializer for which no serializer exists and expects an error to get raised."""
    _SERIALIZERS.clear()
    try:
        add_serializer(int, lambda: 1)  # Add any non-matching serializer so the sequence is not empty.
        get_serializer(str)
    except ValueError:
        ...
    else:
        raise AssertionError()

def test_serialize_callable():
    """Tries to serialize a value for which a callable serializer
    is defined and expects that callable to be used to modify the value."""
    _SERIALIZERS.clear()
    add_serializer(int, lambda _: 1)
    add_serializer(str, lambda _: "a")

    assert serialize(2) == 1
    assert serialize("b") == "a"

def test_serialize_none():
    """Tries to serialize a value for which the serializer is
    `None` and expects the serializer to leave the value as-is."""
    add_serializer(int, None)
    add_serializer(str, None)

    assert serialize(1) == 1
    assert serialize("a") == "a"


if __name__ == '__main__':
    test_manage_serializer()
    test_get_serializer_superclass()
    test_get_serializer_no_exist()
    test_serialize_callable()
    test_serialize_none()