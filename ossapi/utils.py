from enum import EnumMeta

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
