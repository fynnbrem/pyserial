This streamlines the process of serializing and deserializing data in Python.

# Motivation

When working with serialization, one often hits the limitation, that only a very limited amount of data types can be actually saved, so one either needs to reduce the spectrum of data types used in the code or create cumbersome, external code to handle the conversion between the types.

![Representation of the workflow of the default and this library's approach to serialization.](https://github.com/fynnbrem/pyserial/blob/master/res/images/banner.png)

This library integrates the code of conversion into the serialized classes themselves and offers plenty of implicit conversion to effortlessly serialize some of the more often used data types of Python.


# Details

This library uses the field-logic provided by `dataclasses` to not just create a simple field, but a *serializable* field that automatically marks the field for serialization and can be provided with additional arguments for more specific needs.

# Usage

To create your own serializable class `MyClass`, you need to follow these 3 steps:
1. Decorate your class with the stdlib `dataclass`:
```Python
from dataclasses import dataclass

@dataclass
class MyClass:
    ...
```
2. Add the mixin `Serializable` provided by this library:
```Python
from dataclasses import dataclass
from pyserial import Serializable

@dataclass
class MyClass(Serializable):
    ...
```
3. Instantiate any fields you want serialized with as `SerialField`, just like you would with `dataclassses.field`:
```Python
from dataclasses import dataclass
from pyserial import Serializable, SerialField

@dataclass
class MyClass(Serializable):
    my_str: str = SerialField()
    my_tuple: tuple = SerialField()
```

Now you have a simple class, which can be easily serialized with the methods provided my `Serializable`.
For more details, for example on handling complex type annotations, refer to the documentation of the classes themselves.

