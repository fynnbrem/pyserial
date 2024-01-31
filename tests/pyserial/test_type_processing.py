from types import NoneType
# noinspection PyUnresolvedReferences
from typing import Union, Optional

from pyserial.type_processing import is_optional, is_singular_optional, type_to_list


def test_is_optional():
    """Test if types of various nestings and size are considered optional."""

    def test(type_, is_opt):
        assert is_optional(type_) == is_opt

    # region: Different definitions
    test(Optional[int], True)
    test(Union[int, None], True)
    test(Union[int, NoneType], True)
    # endregion
    # region: Nested definitions
    test(Optional[Union[int, str]], True)
    test(Union[Optional[str], int], True)

    # endregion
    # region: Different orders
    test(Union[None, int, str], True)
    test(Union[int, None, str], True)
    # endregion
    # region: Non-optionals
    test(int, False)
    test(Union[int, str], False)
    test(list[int], False)
    test(list[Optional[int]], False)
    # endregion


def test_is_singular_optional():
    """Test if types of various nestings and size are considered singular optional."""

    def test(type_, is_opt):
        assert is_singular_optional(type_) == is_opt

    test(Optional[int], True)
    test(Optional[Union[int, str]], False)
    test(Optional, False)
    test(Union[int, str, None], False)

def test_type_to_list():
    """Tests that different nestings and singular optionals get converted correctly."""
    def test(type_, expected_list):
        assert type_to_list(type_) == expected_list
    # region: Different nesting depths
    test(int, [int])
    test(list[int], [list, int])
    test(list[tuple[int]], [list, tuple, int])
    test(list[tuple[list[int]]], [list, tuple, list, int])
    # endregion
    # region: Optionals
    test(Optional[int], [(int, None)])
    test(Union[int, None], [(int, None)])
    test(Union[None, int], [(int, None)])

    test(list[Optional[int]], [list, (int, None)])
    # endregion

def test_type_to_list_too_complex():
    """Tests that types with too complex nestings raise an error"""
    def test(type_):
        try:
            type_to_list(type_)
        except ValueError:
            ...
        else:
            raise AssertionError()

    test(Union[str, int])
    test(list[Union[str, int]])
    test(Union[str, int, None])
    test(list[Optional[list[Union[str, int, None]]]])

if __name__ == '__main__':
    test_is_optional()
    test_is_singular_optional()
    test_type_to_list()
    test_type_to_list_too_complex()
