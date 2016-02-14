#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Singleton Mixin"""

def hsh(cls):
    return str(hash(cls))

class Singleton(object):
    """Singleton Mixin Class
    Inherit this class and make the subclass Singleton.
    Usage:
        >>> class A(object):
        ...     pass
        >>> class B(Singleton):
        ...     pass
        >>> a1 = A()
        >>> a2 = A()
        >>> b1 = B()    # Create instance as usual
        >>> b2 = B()
        >>> a1 == a2    # a1, a2 are not singleton
        False
        >>> b1 == b2    # b1, b2 are singleton
        True
    """
    def __new__(cls, *args, **kwargs):
        # Store instance on cls._instance_dict with cls hash
        key = hsh(cls)
        if not hasattr(cls, '_instance_dict'):
            cls._instance_dict = {}
        if key not in cls._instance_dict:
            cls._instance_dict[key] = \
                super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance_dict[key]

    def __init__(self, *a, **kw):
        if kw.pop('is_configured', False):
            return
        self.init(*a, **kw)

    def init(self, *a, **kw):
        raise NotImplemented("override this method")

    @classmethod
    def instance(cls, *a, **kw):
        kw['is_configured'] = hsh(cls) in getattr(cls, '_instance_dict', {}) 
        return cls(*a, **kw)