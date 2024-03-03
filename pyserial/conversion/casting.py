# noinspection PyUnresolvedReferences
from typing import Union, Optional, Iterable, Any, Callable, TypeVar, get_origin, Tuple

from pyserial.conversion.enum_conversion import SerializableEnum
from pyserial.conversion.type_processing import type_to_list

T = TypeVar("T")
Caster = Callable[[Any], T]


def optional_caster(func: Caster[T]) -> Caster[Optional[T]]:
    """Converts a caster to a caster that will retain `None` as value."""

    def inner(value: Any):
        if value is None:
            return None
        else:
            return func(value)

    return inner


def get_caster(type_: T) -> Caster[T]:
    """Gets a caster for a certain type.
    - For Serializable, this is `.deserialize`
    - For simple types, this is the type itself
    - For generic types, this is a dedicated caster to cast nested types (See `get_caster_for_generic_type`).
    """
    from pyserial import Serializable
    # region: Delegate caster acquisition depending on the type.
    # In the first case, the type is simple and can be used as caster as-is.
    # In the second case, the type is generic and must be processed into simple types first.
    if get_origin(type_) is None:  # Simple types have no origin.
        if issubclass(type_, (Serializable, SerializableEnum)):
            caster = type_.deserialize
        elif callable(type_):
            caster = type_
        else:
            raise ValueError(f"Cannot get a caster for the simple type `{type_}` as it is not callable.")
    else:
        try:
            caster = get_caster_for_generic_type(type_)
        except ValueError as err:
            raise ValueError(f"Cannot get deserializer for {type_}.") from err
    # endregion
    return caster


def get_caster_for_generic_type(type_: T) -> Caster[T]:
    """Creates a caster based on a generic type (a parameterized type like `list[str]`).
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


def get_caster_from_type_list(types: Iterable[Union[type, Tuple[type, None]]]) -> Caster:
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
    optional = False
    if isinstance(current_type, tuple):
        current_type, _ = current_type
        optional = True

    def inner(value: Any):
        if issubclass(current_type, Iterable) and not issubclass(current_type, str):
            items = [get_caster_from_type_list(types)(item) for item in value]
            casted = get_caster(current_type)(items)
        else:
            casted = get_caster(current_type)(value)
        return casted

    if optional:
        return optional_caster(inner)
    else:
        return inner


if __name__ == '__main__':
    d = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    t_func = get_caster(tuple[list[str]])
    v = t_func(d)
    print(v)
