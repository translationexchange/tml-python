import functools
import warnings


def deprecated(fn):
    """ This is a decorator that marks functions as deprecated. It will result in a warning being emitted when the function is used.
        Usage:
            @deprecated
            def my_func():
                pass
    """

    @functools.wraps(fn)
    def wrapper(*a, **kw):
        msg = 'Call to deprecated function {}'.format(fn.__name__)
        warnings.warn_explicit(msg,
            category=DeprecationWarning,
            filename=fn.func_code.co_filename,
            lineno=fn.func_code.co_firstlineno + 1)
        return fn(*a, **kw)
    return wrapper


def enable_warnings():
    warnings.simplefilter('always', DeprecationWarning)