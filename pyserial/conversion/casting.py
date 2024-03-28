import datetime
# noinspection PyUnresolvedReferences
from typing import List, Union, Optional, Iterable, Any, Callable, TypeVar, get_origin, Tuple

from pyserial.conversion.enum_conversion import SerializableEnum
from pyserial.conversion.serialization import SerialDict, serializer_func
from pyserial.conversion.type_processing import type_to_list

T = TypeVar("T")
Caster = Callable[[Any], T]

_CASTERS: List[Tuple[type, Optional[Callable[[Union[str, int, float, list, SerialDict]], Any]]]] = [
	(type(None), None),
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


def add_caster(type_: type, caster: Callable[[Union[str, int, float, list, SerialDict]], Any]):
	"""Adds the `caster` for the `type_` to `_CASTERS` while retaining the desired order of that list."""
	for index, (compare_type, _) in enumerate(_CASTERS):
		if compare_type is None:
			continue
		if compare_type == type_:
			_CASTERS[index] = (type_, caster)
			return
		elif issubclass(type_, compare_type):
			_CASTERS.insert(index, (type_, caster))
			return
	_CASTERS.append((type_, caster))


def _get_caster(type_: type) -> Optional[Callable[[Union[str, int, float, list, SerialDict]], Any]]:
	"""Gets the caster for the `type_` if listed in `_CASTERS`.

	Returns `None` if there is no registered caster for this type.

	When there are multiple possible casters defined due to subclassing,
	the deepest, matching subclass is taken for the deserializer."""
	for key, caster in _CASTERS:
		# ↑ The promise of returning the deepest, matching subclass is granted by the order of `_SERIALIZERS`.
		if issubclass(type_, key):
			return caster
	return None


def caster_func(*types: type):
	"""A decorator that adds the decorated function to `_CASTERS` using `add_caster()`."""

	def inner(func: Callable):
		for type_ in types:
			add_caster(type_, func)
		return func

	return inner


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
	from pyserial.serializable import Serializable
	# region: Delegate caster acquisition depending on the type.
	# In the first case, the type is simple and can be used as caster as-is.
	# In the second case, the type is generic and must be processed into simple types first.
	if get_origin(type_) is None:  # Simple types have no origin.
		registered_caster = _get_caster(type_)
		if registered_caster is not None:
			caster = registered_caster
		elif issubclass(type_, (Serializable, SerializableEnum)):
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


@caster_func(datetime.datetime)
def run(date: str) -> datetime.datetime:
	"""Lists and tuples will both be cast into a `list` and their items will be serialized."""
	return datetime.datetime.fromisoformat(date)


if __name__ == '__main__':
	d = [
		[1, 2, 3],
		[4, 5, 6],
		[7, 8, 9]
	]
	t_func = get_caster(tuple[list[str]])
	v = t_func(d)
	print(v)
