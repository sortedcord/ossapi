from enum import EnumMeta, Enum, IntFlag
from datetime import datetime, timezone
from typing import Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing_utils import get_args, get_origin

def is_high_model_type(type_):
    """
    Whether ``type_`` is both a model type and not a base model type.

    "high" here is meant to indicate that it is not at the bottom of the model
    hierarchy, ie not a "base" model.
    """
    return is_model_type(type_) and not is_base_model_type(type_)

def is_model_type(type_):
    """
    Whether ``type_`` is a subclass of ``Model``.
    """
    if not isinstance(type_, type):
        return False
    return issubclass(type_, Model)

def is_base_model_type(type_):
    """
    Whether ``type_`` is a subclass of ``BaseModel``.
    """
    if not isinstance(type_, type):
        return False
    return issubclass(type_, BaseModel)

class Model:
    """
    Base class for all models in ``ossapi``. If you want a model which handles
    its own members and cleanup after instantion, subclass ``BaseModel``
    instead.
    """
    def override_types(self):
        """
        Sometimes, the types of attributes in models depends on the value of
        other fields in that model. By overriding this method, models can return
        "override types", which overrides the static annotation of attributes
        and tells ossapi to use the returned type to instantiate the attribute
        instead.

        This method should return a mapping of ``attribute_name`` to
        ``intended_type``.
        """
        return {}

    @classmethod
    def override_class(cls, _data):
        """
        This method addressess a shortcoming in ``override_types`` in order to
        achieve full coverage of the intended feature of overriding types.

        The model that we want to override types for may be at the very top of
        the hierarchy, meaning we can't go any higher and find a model for which
        we can override ``override_types`` to customize this class' type.

        A possible solution for this is to create a wrapper class one step above
        it; however, this is both dirty and may not work (I haven't actually
        tried it). So this method provides a way for a model to override its
        *own* type (ie class) at run-time.
        """
        return None

class BaseModel(Model):
    """
    A model which promises to take care of its own members and cleanup, after we
    instantiate it.

    Normally, for a high (non-base) model type, we recurse down its members to
    look for more model types after we instantiate it. We also resolve
    annotations for its members after instantion. None of that happens with a
    base model; we hand off the model's data to it and do nothing more.

    A commonly used example of a base model type is an ``Enum``. Enums have
    their own magic that takes care of cleaning the data upon instantiation
    (taking a string and converting it into one of a finite set of enum members,
    for instance). We don't need or want to do anything else with an enum after
    instantiating it, hence it's defined as a base type.
    """
    pass

class EnumModel(BaseModel, Enum):
    pass

class IntFlagModel(BaseModel, IntFlag):
    pass


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


class Datetime(datetime, BaseModel):
    """
    Our replacement for the ``datetime`` object that deals with the various
    datetime formats the api returns.
    """
    def __new__(cls, value): # pylint: disable=signature-differs
        if value is None:
            raise ValueError("cannot instantiate a Datetime with a null value")
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

# whenever a dataclass gets created, ``dataclasses`` traverses up the
# inheritance hierarchy and looks for any class which is a dataclass. If it
# finds one, it adds the parameters for that class to the new dataclass'
# __init__.
# Since almost all of our models are dataclasses, this means that
# ``RequiresAPI`` also needs to be a dataclass so that the new ``_api``
# parameter gets picked up and added to the created ``__init__``.

@dataclass
class RequiresAPI:
    """
    A mixin for models which require api access after instantiation. Typically
    this is to allow the model to expose a public method which retrieves some
    additional information from the api, without requiring the user to pass an
    api instance.

    Models which subclass this can expect an ``_api`` attribute to be available
    to them, which is the ``OssapiV2`` instance that loaded that model.
    """
    # can't annotate with OssapiV2 or we get a circular import error, this is
    # good enough
    _api: field()

class Expandable(RequiresAPI, ABC):
    """
    A mixin for models which can be "expanded" to a different model which has a
    superset of attributes of the current model. Typically this expansion is
    expensive (requires an additional api call) which is why it is not done by
    default.
    """

    @abstractmethod
    def expand(self):
        pass

@dataclass
class PaginatedModel(RequiresAPI, ABC):
    cursor: field()

    @abstractmethod
    def next(self):
        pass

    def can_paginate(self):
        return bool(self.cursor)


# typing utils
# ------------

def is_optional(type_):
    """
    ``Optional[X]`` is equivalent to ``Union[X, None]``.
    """
    return get_origin(type_) is Union and get_args(type_)[1] is type(None)

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

def flat_types(type_):
    """
    Returns the "flattened" version of the type hint ``type_``. Analogous to
    flattening a nested list, where the nesting in this case is caused by the
    ``Union`` type.

    Examples
    --------
    >>> flat_types(Union[int, None])
    [<class 'int'>, <class 'NoneType'>]
    >>> flat_types(Optional[int])
    [<class 'int'>, <class 'NoneType'>]
    >>> flat_types(Union[int, Union[Union[str, int], float], \
            Tuple[Optional[int], int]])
    [<class 'int'>, <class 'str'>, <class 'float'>,
        typing.Tuple[typing.Optional[int], int]]
    """
    if get_origin(type_) is not Union:
        return [type_]

    args = get_args(type_)
    ret = []
    for arg in args:
        ret += flat_types(arg)
    return ret
