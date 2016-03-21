import os
import logging
import logging.handlers
import functools
import json
import gzip
import tarfile
from copy import copy
from codecs import open
from contextlib import contextmanager
from six import StringIO, functools, string_types
import warnings
from datetime import datetime, timedelta
from time import mktime
from .strings import to_string

reduce = functools.reduce

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

def merge_opts(a, **b):
    """Creates shallow copy from source and updates with kwargs"""
    c = copy(a)
    c.update(b)
    return c

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

def untar(source_file, dest_path='.'):
    if isinstance(source_file, string_types):   # we deal with path
        assert source_file.endswith('tar.gz'), "`source_file` path should end with `tar.gz` if provided as path"
        source_file = tarfile.open(source_file)
    assert isinstance(source_file, tarfile.TarFile), "`source_file` have to be an instance of `tarfile.TarFile`"
    source_file.extractall(dest_path)
    source_file.close()


def read_json(path):
    with open(path, 'rb', encoding='utf-8') as fp:
        return json.loads(to_string(fp.read()))


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class chdir(object):
    """
    Step into a directory temporarily.
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        os.chdir(self.old_dir)


def rm_symlink(path):
    if os.path.realpath(path) != path:
        target_path = os.path.realpath(path)
    if os.path.exists(path):
        os.remove(path)
