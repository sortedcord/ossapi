from enum import EnumMeta

class ListEnumMeta(EnumMeta):
    """
    Allows an enum to be instantiated with a list of members of the enum. So
    `PlayStyles([1, 8])` is equivalent to `PlayStyles.MOUSE | PlayStyles.TOUCH`.
    """
    def __call__(cls, value, names=None, *, module=None, qualname=None, type=None, start=1):
        if not isinstance(value, list):
            return super().__call__(value, names, module=module, qualname=qualname, type=type, start=start)
        value = iter(value)
        val = next(value)
        new_val = super().__call__(val, names, module=module, qualname=qualname, type=type, start=start)
        for val in value:
            val = super().__call__(val, names, module=module, qualname=qualname, type=type, start=start)
            new_val |= val
        return new_val
