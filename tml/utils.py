import os
import logging
import logging.handlers
import functools
import json
import gzip
from StringIO import StringIO
import warnings
from datetime import datetime, timedelta
from time import mktime

pj = os.path.join

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def rel(*x):
    return pj(os.path.abspath(BASE_DIR), *x)

APP_DIR = rel('tml')


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


def merge(a, b):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a

multi_merge = functools.partial(reduce, merge)


def ts():
    return int(mktime(datetime.utcnow().timetuple()))


def cookie_name(app_key):
    return 'trex_%s' % app_key


def decode_cookie(base64_payload, secret=None):
    try:
        data = json.loads(base64.b64decode(base64_payload))
        # TODO: Verify signature
        return data
    except Exception as e:
        raise CookieNotParsed(e)


def interval_timestamp(interval):
    t = ts()
    return t - (t % interval)


def read_gzip(payload):
    buf = StringIO(payload)
    buf.seek(0)
    gzip_f = gzip.GzipFile(fileobj=buf, mode='rb')
    return gzip_f.read()
