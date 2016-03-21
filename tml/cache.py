from __future__ import absolute_import
# encoding: UTF-8
import os
from six import string_types
from importlib import import_module
from types import FunctionType
from six.moves.urllib.parse import urlencode
from .base import SingletonMixin
from .config import CONFIG
from .utils import interval_timestamp, ts, rel
from .logger import LoggerMixin, get_logger


__author__ = 'a@toukmanov.ru, xepa4ep'


class CacheVersion(LoggerMixin):

    version = None
    cache = None

    CACHE_VERSION_KEY = 'current_version'

    def __init__(self, cache, version=None, key=None):
        self.cache = cache
        self.version = version
        self._key = self.CACHE_VERSION_KEY if key is None else key
        super(CacheVersion, self).__init__()

    def set(self, new_version):
        self.version = new_version

    def reset(self):
        self.version = None

    def upgrade(self):
        self.cache.store(self._key, {'version': 'undefined', 't': self.cache_timestamp})
        self.reset()

    invalidate = upgrade

    @property
    def cache_timestamp(self):
        return interval_timestamp(CONFIG['version_check_interval'])

    def validate_version(self, version):
        if not version or not type(version.get('t', None)) is int:
            return 'undefined'
        expires_at = version['t'] + CONFIG['version_check_interval']
        if expires_at < ts():
            self.debug('Cache version is outdated')
            return 'undefined'
        else:
            delta = expires_at - ts()
            self.debug('Cache version is up to date, expires in %s', delta)
            return version['version']

    def fetch(self):

        def on_miss(_):
            return {'version': CONFIG.cache.get('version', 'undefined'),
                    't': self.cache_timestamp}

        version_obj = self.cache.fetch(self._key,
                                       opts={'miss_callback': on_miss})
        version_obj['version'] = self.version = self.validate_version(version_obj)
        return self.version

    def store(self, new_version):
        self.version = new_version
        self.cache.store(self._key, {'version': new_version, 't': self.cache_timestamp})

    def is_undefined(self):
        return self.version is None or self.version == 'undefined'

    def is_defined(self):
        return not self.is_undefined()

    def is_invalid(self):
        try:
            ('undefined', '0', 'None').index(str(self.version))
            return True
        except:
            return False

    def is_valid(self):
        return not self.is_invalid()

    def versioned_key(self, key, namespace=''):
        version = '' if key == self._key else '_v#%s' % self.version
        return "tml_%s:%s_%s" % (namespace, version, key)

    def __str__(self):
        return self.version


class CachedClient(SingletonMixin, LoggerMixin):

    default_adapter_module = 'tml.cache_adapters'
    version_attr = '__cache_version__'
    _instance_dict = {}

    def __init__(self, *args, **kwargs):
        LoggerMixin.__init__(self)

    @classmethod
    def instance(cls, **kwargs):
        if CONFIG.cache_enabled():
            klass_path = kwargs.get('adapter', CONFIG.cache.get('adapter', None))
            return cls.load_adapter(klass_path, **kwargs)
        else:
            return CachedClient()

    @classmethod
    def default_dir(cls):
        return CONFIG['cache'].get('path', rel('tml/cache'))

    @classmethod
    def load_adapter(cls, klass, **kwargs):
        def build_cache(klass, *bases):
            return type(
                klass.__name__,
                bases + (CachedClient,),
                dict(klass.__dict__))

        if type(klass) is FunctionType:
            return klass()
        elif isinstance(klass, string_types):
            path_parts = klass.split('.')
            if len(path_parts) == 1:  # for shorter configuration
                path_parts = CachedClient.default_adapter_module.split('.') +  path_parts
            package_path, adapter_name = '.'.join(path_parts[:-1]), path_parts[-1]
            module = import_module(package_path)
            adapter_class = getattr(module, adapter_name)
            if type(adapter_class) is FunctionType:  # e.g. factory callable
                return adapter_class(build_cache)
            else:
                return build_cache(adapter_class)()
        else:  # custom object
            if isinstance(klass, type):
                return build_cache(klass)()
            else:  # object
                return klass

    @property
    def version(self):
        if hasattr(self, CachedClient.version_attr):
            return self._get_version()
        setattr(self, CachedClient.version_attr, CacheVersion(self))
        return self._get_version()

    @property
    def namespace(self):
        ns = CONFIG.cache.get('namespace', None)
        if not ns:
            ns = CONFIG.access_token(default=CONFIG.application_key())[:5]
        return ns

    def versioned_key(self, key, opts=None):
        return self.version.versioned_key(key, self.namespace)

    def fetch(self, key, opts=None):
        pass

    def store(self, key, data, opts=None):
        pass

    def delete(self, key, opts=None):
        pass

    def exists(self, key, opts=None):
        pass

    def clear(self):
        pass

    def read_only(self):
        return False

    def reset_version(self):
        self.version.reset()

    def upgrade_version(self):
        self.version.upgrade()

    def store_version(self, new_version):
        self.version.store(new_version)

    def _get_version(self):
        return getattr(self, CachedClient.version_attr, None)
