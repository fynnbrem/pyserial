"""Functions and data to handle the serialization process itself.
Also stores the `_SERIALIZERS` used in the process."""
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Callable, Any, Iterable

SerialDict = dict[str, Union[str, int, float, list, dict]]
SerialTypes = [str, int, float, list, SerialDict]
_SERIALIZERS: list[tuple[type, Optional[Callable[[Any], Union[*SerialTypes]]]]] = [
    (None, None),
    (str, None),
    (int, None),
    (float, None),

]
"""The list of existing serializers.
Each item is a tuple with the first item being the type this
 serializer corresponds to and the the second being the serializer itself.
They are ordered in such a way, that subclassses of any class always come before that class.

For `str`, `int` and `float`, the serializer is `None` as these values can be serialized as they are.

To retain that order, only use `add_serializer()`/`@serializer_func()` to add entries to this list."""


def add_serializer(type_: type, serializer: Callable[[Any], Union[*SerialTypes]]):
    """Adds the `serializer` for the `type_` to `SERIALIZERS` while retaining the desired order of that list."""
    for index, (compare_type, _) in enumerate(_SERIALIZERS):
        if compare_type is None:
            continue
        if compare_type == type_:
            _SERIALIZERS[index] = (type_, serializer)
            return
        elif issubclass(type_, compare_type):
            _SERIALIZERS.insert(index, (type_, serializer))
            return
    _SERIALIZERS.append((type_, serializer))


def get_serializer(type_: type):
    """Gets the serializer for the `value`.
    When there are multiple possible serializers defined due to subclassing,
     the deepest, matching subclass is taken for the deserializer."""
    for key, serializer in _SERIALIZERS:
        # ↑ The promise of returning the deepest, matching subclass is granted by the order of `_SERIALIZERS`.
        if issubclass(type_, key):
            return serializer
    raise ValueError(f"There is no serializer defined for `{type_}`")


def serialize(value: Any) -> SerialTypes:
    """Recursively serialize the value. Uses the serializers defined in `_SERIALIZERS`."""
    serializer = get_serializer(type(value))
    if serializer is None:
        return value
    else:
        return serializer(value)


def serializer_func(*types: type):
    """A decorator that adds the decorated function to `_SERIALIZERS` using `add_serializer()`."""

    def inner(func: Callable):
        for type_ in types:
            add_serializer(type_, func)
        return func

    return inner


@serializer_func(list, tuple)
def run(iterable: Iterable) -> list:
    """Lists and tuples must both be cast into a `list` and their items must be serialized."""
    new = list()
    for item in iterable:
        new.append(serialize(item))
    return new


@serializer_func(Path)
def run(path: Path) -> str:
    """Paths must be cast into `str`."""
    return str(path)
