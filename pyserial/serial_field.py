from dataclasses import Field, MISSING
# noinspection PyUnresolvedReferences
from typing import Union, Optional


class SerialField(Field):
    def __init__(
            self, *, serialize=True, deserializer=None,
            default=MISSING, default_factory=MISSING, init=True, repr=True,
            hash=None, compare=True, metadata=None, kw_only=MISSING, **kwargs
    ):
        # noinspection PyArgumentList
        super().__init__(
            default=default, default_factory=default_factory, init=init, repr=repr,
            hash=hash, compare=compare, metadata=metadata, kw_only=kw_only, **kwargs
        )
        self.serialize = serialize
        self.deserializer = deserializer
