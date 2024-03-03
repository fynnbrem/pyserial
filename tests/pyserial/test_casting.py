from dataclasses import dataclass
# noinspection PyUnresolvedReferences
from typing import Union, Optional, Any, Iterable, Tuple
from unittest.mock import Mock

from pyserial.casting import optional_caster, get_caster_from_type_list


def test_optional_caster():
    """Pass in a simple function and assert that the new caster converts
    `None` to `None` and delegates not-`None` to the former caster."""
    func = Mock()

    caster = optional_caster(func)
    assert caster(None) is None
    caster(1)
    func.assert_called_once_with(1)


def test_get_caster_from_type_list():
    @dataclass
    class TestSet():
        types: Iterable[Union[type, Tuple[type, None]]]
        input_data: Any
        casted_data: Any
        case: str

    def test(test_set: TestSet):
        caster = get_caster_from_type_list(test_set.types)
        result = caster(test_set.input_data)
        assert result == test_set.casted_data, test_set.case

    test_sets = [
        TestSet(
            types=(list, tuple, str),
            input_data=[
                [1, 2],
                [3, 4],
                [5]
            ],
            casted_data=[
                ("1", "2"),
                ("3", "4"),
                ("5",)
            ],
            case="Nesting of simple types"
        ),
        TestSet(
            types=(tuple, list, str),
            input_data=[
                [1, 2],
                [3, 4],
                [5]
            ],
            casted_data=(
                ["1", "2"],
                ["3", "4"],
                ["5"]
            ),
            case="Nesting of simple types"
        ),
        TestSet(
            types=(tuple, tuple),
            input_data=[list(), list(), list()],
            casted_data=(tuple(), tuple(), tuple()),
            case="Nesting of simple types without a scalar and lowest level"
        ),
        TestSet(
            types=(str,),
            input_data=1,
            casted_data="1",
            case="Single type"
        ),
        TestSet(
            types=((str, None),),
            input_data=1,
            casted_data="1",
            case="Single type with optional"
        ),
        TestSet(
            types=((str, None),),
            input_data=None,
            casted_data=None,
            case="Single type with optional"
        ),
        TestSet(
            types=(tuple, (str, None),),
            input_data=[1, None, 3],
            casted_data=("1", None, "3"),
            case="Nesting with optional"
        )

    ]

    for test_set_ in test_sets:
        test(test_set_)


if __name__ == '__main__':
    test_optional_caster()
    test_get_caster_from_type_list()
