from enum import EnumMeta, Enum
from datetime import datetime, timezone
from typing import get_args, get_origin, Union
import dataclasses

from ossapi.mod import Mod

class ListEnumMeta(EnumMeta):
    """
    Allows an enum to be instantiated with a list of members of the enum. So
    ``MyEnum([1, 8])`` is equivalent to ``MyEnum(1) | MyEnum(8)``.
    """
    def __call__(cls, value, names=None, *, module=None, qualname=None,
        type_=None, start=1):

        def _instantiate(value):
            # interestingly, the full form of super is required here (instead of
            # just ``super().__call__``). I guess it's binding to this inner
            # method instead of the class?
            return super(ListEnumMeta, cls).__call__(value, names,
                module=module, qualname=qualname, type=type_, start=start)

        if not isinstance(value, list):
            return _instantiate(value)
        value = iter(value)
        val = next(value)
        new_val = _instantiate(val)
        for val in value:
            val = _instantiate(val)
            new_val |= val
        return new_val


class Datetime(datetime):
    """
    Our replacement for the ``datetime`` object that deals with the various
    datetime formats the api returns.
    """
    def __new__(cls, value):
        # the api returns a bunch of different timestamps: two ISO 8601
        # formats (eg "2018-09-11T08:45:49.000000Z" and
        # "2014-05-18T17:22:23+00:00"), a unix timestamp (eg
        # 1615385278000), and others. We handle each case below.
        # Fully compliant ISO 8601 parsing is apparently a pain, and
        # the proper way to do this would be to use a third party
        # library, but I don't want to add any dependencies. This
        # stopgap seems to work for now, but may break in the future if
        # the api changes the timestamps they return.
        # see https://stackoverflow.com/q/969285.
        if value.endswith("Z"):
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        if value.isdigit():
            # see if it's an int first, if so it's a unix timestamp. The
            # api returns the timestamp in milliseconds but
            # ``datetime.fromtimestamp`` expects it in seconds, so
            # divide by 1000 to convert.
            value = int(value) / 1000
            return datetime.fromtimestamp(value, tz=timezone.utc)
        if cls._matches_datetime(value, "%Y-%m-%dT%H:%M:%S%z"):
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
        if cls._matches_datetime(value, "%Y-%m-%d"):
            return datetime.strptime(value, "%Y-%m-%d")

    @staticmethod
    def _matches_datetime(value, format_):
        try:
            _ = datetime.strptime(value, format_)
        except ValueError:
            return False
        return True

# typing utils
# ------------

def is_optional(type_):
    """
    ``Optional[X]`` is equivalent to ``Union[X, None]``.
    """
    return get_origin(type_) is Union and get_args(type_)[1] is type(None)

def is_model_type(type_):
    # almost every model we have is a dataclass, but we do have a few unique
    # ones which we also need to consider as a model type.

    # imported here to avoid a circular import
    from ossapi.models import Cursor, _Event
    return type_ in [Cursor, _Event] or dataclasses.is_dataclass(type_)

def is_base_type(type_):
    """
    A "base" type is a type that is still instantiable (so not a primitive)
    but one that we don't need to recurse down its members to look for more
    model types (or more base types). The base type is responsible for
    cleaning up and/or modifying the data we give it, and we move on after
    instantiating it.
    Examples are enums, mods, and datetimes.
    """
    if not isinstance(type_, type):
        return False
    return issubclass(type_, (Enum, datetime, Mod))

def is_primitive_type(type_):
    if not isinstance(type_, type):
        return False
    return type_ in [int, float, str, bool]

def is_compatible_type(value, type_):
    # make an exception for an integer being instantiated as a float. In
    # the json we receive, eg ``pp`` can have a value of ``15833``, which is
    # interpreted as an int by our json parser even though ``pp`` is a
    # float.
    if type_ is float and isinstance(value, int):
        return True
    return isinstance(value, type_)
