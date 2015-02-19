
def cached_property(fn):
    """ Cached property method decorator """
    @property
    def tmp(self, *args):
        field_name = '_%s' % f.__name__
        try:
            cached = getattr(self, field_name)
            if not cached is None:
                return cached
        except AttributeError:
            pass
        ret = f(self, *args)
        setattr(self, field_name, ret)
        return ret
    return tmp
