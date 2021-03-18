from enum import EnumMeta, Enum
from datetime import datetime
from abc import abstractmethod

class Formattable:
    @abstractmethod
    def format(self):
        pass

# "Formattable Enum"
class FEnum(Formattable, Enum):
    def format(self):
        return self.value


class ListEnumMeta(EnumMeta):
    """
    Allows an enum to be instantiated with a list of members of the enum. So
    `PlayStyles([1, 8])` is equivalent to `PlayStyles.MOUSE | PlayStyles.TOUCH`.
    """
    def __call__(cls, value, names=None, *, module=None, qualname=None,
        type=None, start=1):

        def _instantiate(value):
            # interestingly, the full form of super is required here (instead of
            # just ``super().__call__``). I guess it's binding to this inner
            # method instead of the class?
            return super(ListEnumMeta, cls).__call__(value, names,
                module=module, qualname=qualname, type=type, start=start)

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
            # ``datetime.utcfromtimestamp`` expects it in seconds, so
            # divide by 1000 to convert.
            value = int(value) / 1000
            return datetime.utcfromtimestamp(value)
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
