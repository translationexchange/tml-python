import ctypes
import datetime
import six
import __builtin__
from .ext import date as date_exts, lst as list_exts
from .logger import get_logger


_get_dict = ctypes.pythonapi._PyObject_GetDictPtr
_get_dict.restype = ctypes.POINTER(ctypes.py_object)
_get_dict.argtypes = [ctypes.py_object]


def patch_types():
    # datetime.date
    patch_type(datetime.date, date_exts)
    # __builtin__.list
    patch_type(__builtin__.list, list_exts)


def patch_type(module, exts):
    d = _get_dict(module)[0]
    for method_name, method in six.iteritems(exts):
        d[method_name] = method

    logger = get_logger()
    logger.debug("PATCH: module `%s` extended with %s", module, ', '.join(exts.keys()))

