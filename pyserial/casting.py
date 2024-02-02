# noinspection PyUnresolvedReferences
from typing import Union, Optional, Iterable, Any, Callable, TypeVar

from pyserial.type_processing import type_to_list

T = TypeVar("T", bound=type)
Caster = Callable[[Any], T]


def get_caster(type_: T) -> Caster[T]:
    """Gets a caster for a certain type.
    - For native types, this is the type itself
    - For Serializable, this is `.deserialize`
    - For complex types, this is a dedicated caster to cast nested types (See `get_caster_for_complex_type`).
    """
    from pyserial import Serializable
    if issubclass(type_, Serializable):
        caster = type_.deserialize
    elif isinstance(type_, type):
        caster = type_
    else:
        try:
            caster = get_caster_for_complex_type(type_)
        except ValueError as err:
            raise ValueError(f"Cannot get deserializer for {type_}.") from err
    return caster


def get_caster_for_complex_type(type_: T) -> Caster[T]:
    """Creates a caster based on a complex type (a subscripted type).
    The caster will cast iterables nested into each other and their final items into the types defined by the
    `type_`.

    Works by separating the complex type into list items and calling it on `get_caster_from_type_list()`.

    Limitations
    ===========
    The same limitations for the `type_` as in `type_to_list` apply.

    Examples
    ========
    ```
    caster = get_caster_from_type_list((tuple, list, str))
    d = [
        [1, 2, 3],
        [4, 5, 6],
    ]
    d = caster(d)
    > d = (
        ["1", "2", "3"],
        ["4", "5", "6"],
    )
    ```
    """
    types = type_to_list(type_)
    caster = get_caster_from_type_list(types)
    return caster


def get_caster_from_type_list(types: Iterable[Union[type, tuple[Callable, None]]]) -> Caster:
    """Creates a caster based on a list of types.
    The caster will cast iterables nested into each other and their final items into the types defined by the
    `types`.

    Examples
    ========
    ```
    caster = get_caster_from_type_list((tuple, list, str))
    d = [
        [1, 2, 3],
        [4, 5, 6],
    ]
    d = caster(d)
    > d = (
        ["1", "2", "3"],
        ["4", "5", "6"],
    )
    ```

    :param types:
        A list of types. Each must be a non-subscripted type.
        Unions are not possible here as the casting would be ambiguous in most cases.
        For optional types, you can provide a tuple as item in the list as such: `(your_type, None)`.
    """

    current_type, *types = types

    def inner(value: Any):
        if issubclass(current_type, Iterable) and not issubclass(current_type, str):
            items = [get_caster_from_type_list(types)(item) for item in value]
            casted = get_caster(current_type)(items)
        else:
            casted = get_caster(current_type)(value)
        return casted

    return inner


if __name__ == '__main__':
    d = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    func = get_caster(tuple[list[str]])
    v = func(d)
    print(v)
