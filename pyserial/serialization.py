from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Callable, Any, Iterable


SerialDict = dict[str, Union[str, int, float, list, dict]]
_SERIALIZERS: list[tuple[type, Union[Callable, None]]] = [
    (str, None),
    (int, None),
    (float, None),
]


def add_serializer(type_, serializer):
    for index, (compare_type, _) in enumerate(_SERIALIZERS):
        if compare_type == type_:
            _SERIALIZERS[index] = (type_, serializer)
            return
        elif issubclass(type_, compare_type):
            _SERIALIZERS.insert(index, (type_, serializer))
            return
    _SERIALIZERS.insert(0, (type_, serializer))


def get_serializer(value: Any):
    for key, serializer in _SERIALIZERS:
        if isinstance(value, key):
            return serializer
    raise ValueError(f"There is no serializer defined for `{type(value)}`")


def serialize(value: Any):
    serializer = get_serializer(value)
    if serializer is None:
        return value
    else:
        return serializer(value)


def serializer_func(*types: type):
    def inner(func: Callable):
        for type_ in types:
            add_serializer(type_, func)
        return func

    return inner


@serializer_func(list, tuple)
def run(iterable: Iterable) -> list:
    new = list()
    for item in iterable:
        new.append(serialize(item))
    return new


@serializer_func(Path)
def run(path: Path) -> str:
    return str(path)
