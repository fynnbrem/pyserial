"""Helps in handling complex, nested types.
Primary content is the function `type_to_list()` to convert nested types into a more native format.
"""
from types import NoneType
# noinspection PyUnresolvedReferences
from typing import Union, Optional, get_args, get_origin


def type_to_list(type_: type):
    """Converts nested types into a flat list of these nestings.
    Unions will not be converted as this would potentially cause non-flat lists.
    The only exception are optional types, which will result in their type being expressed as a tuple `(<type>, None)`.

    Limitations
    ===========
    Only works for types which nest a singular type, i.e. `list` but not `dict`.

    Examples
    ========
    type_to_list(list[str])
    [list, str]
    type_to_list(tuple[Optional[int]])
    [tuple, (int, None)]


    :raises ValueError:
        When there is a non-optional union in the type.
    """
    if is_singular_optional(type_):
        type_ = next(arg for arg in get_args(type_) if arg is not NoneType)
        type_tuple = [(get_type_class(type_), None)]
    else:
        type_tuple = [get_type_class(type_)]

    nested_types = get_args(type_)
    if len(nested_types) == 1:
        type_tuple += type_to_list(get_args(type_)[0])
    elif len(nested_types) > 1:
        raise ValueError("Can only create linear lists, so Unions (Except with `NoneType`) are prohibited.")

    return type_tuple


def get_type_class(type_: type):
    """Get the unsubscripted version of a type.
    In contrast to `typing.get_origin()`,
    this returns `type_` if `type_` already is its origin (A non-subscripted type).
    """
    origin = get_origin(type_)
    if origin is None:
        return type_
    else:
        return get_origin(type_)


def is_optional(type_: type) -> bool:
    """Checks if the type is optional, meaning `None` is a valid type for it.
    It does not matter whether the `None` was added by `Optional` or `Union`."""
    # `Optional` is just a shorthand for a `Union` with `None`, so in the backend, both will be converted into the same
    # object, which is a `Union` that contains `None`.
    if get_origin(type_) is not Union:
        return False
    if NoneType not in get_args(type_):
        return False
    return True


def is_singular_optional(type_: type) -> bool:
    """Checks that both apply:
     - If the type is optional, meaning `None` is a valid type for it.
     - The type just consists of two types, `None` and a singular not-`None` type in this case.
    It does not matter whether the `None` was added by `Optional` or `Union`."""
    if len(get_args(type_)) != 2:
        return False
    else:
        return is_optional(type_)


if __name__ == '__main__':
    t_ = tuple[Union[list[str], None]]
    print(type_to_list(t_))
