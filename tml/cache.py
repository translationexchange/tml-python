from __future__ import absolute_import
# encoding: UTF-8
import six
from .api.client import Client
from .config import CONFIG
from .utils import interval_timestamp, ts
try:
    from urllib import urlencode
except ImportError:
    # PY3
    from urllib.parse import urlencode

__author__ = 'a@toukmanov.ru, xepa4ep'

class CacheVersion(object):

    version = None
    cache = None

    CACHE_VERSION_KEY = 'current_version'

    def __init__(self, cache, version=None):
        self.cache = cache
        self.version = version

    def set(self, new_version):
        self.version = new_version

    def upgrade(self):
        self.cache.store(self.CACHE_VERSION_KEY, {'version': 'undefined', 't': self.cache_timestamp})

    invalidate = upgrade

    @property
    def cache_timestamp(self):
        return interval_timestamp(CONFIG['version_check_interval'])

    def validate_version(self, version):
        if not version or not type(version.get('t', None)) is int:
            return False
        expires_at = version['t'] + CONFIG['version_check_interval']
        if expires_at < ts():
            print 'Cache version is outdated'
            return False
        else:
            delta = expires_at - ts()
            print 'Cache version is up to date, expires in %s' % delta
            return version['version']

    def fetch(self):

        def on_miss(_):
            return {'version': CONFIG.cache.get('version', 'undefined'),
                    't': self.cache_timestamp}

        version = self.version = self.cache.fetch(self.CACHE_VERSION_KEY, miss_callback=on_miss)
        return self.validate_version(version)

    def store(self, new_version):
        self.version = new_version
        self.cache.store(self.CACHE_VERSION_KEY, {'version': new_version, 't': self.cache_timestamp})

    def is_undefined(self):
        return not self.version or self.version['version'] == 'undefined'

    def is_defined(self):
        return not self.is_undefined()

    def is_invalid(self):
        return ('undefined', 0).index(self.version) > -1

    def is_valid(self):
        return not self.is_invalid()

    def versioned_key(self, key, namespace=''):
        version = '' if key == self.CACHE_VERSION_KEY else '_v%s' % self.version
        return "tml_%s%s_%s" % (namespace, version, key)


class CachedClient(Singleton):

    default_adapter_module = 'tml.cache_adapters'
    version_attr = '__cache_version__'
    instance_attr = '__instance__'

    @classmethod
    def instance(cls, **kwargs):
        if not hasattr(cls, CachedClient.instance_attr):
            klass_path = CONFIG.cache['adapter']
            adapter = cls.load_adapter(klass_path, **kwargs)
            setattr(self, CachedClient.instance_attr, adapter)
        return getattr(self, CachedClient.instance_attr)

    @classmethod
    def load_adapter(cls, klass, **kwargs):
        if type(klass) is FunctionType:
            return klass()
        elif isinstance(klass, string_types):
            path_parts = klass_path.split('.')
            if len(path_parts) == 1:  # for shorter configuration
                path_parts = CachedClient.default_adapter_module.split('.') +  path_parts
            module_name, class_name = '.'.join(path_parts[:-1]), path_parts[-1]
            module = __import__(module_name, **kwargs)
            adapter_class = getattr(module, class_name)
            return type(class_name, (CachedClient,), dict(adapter_class.__dict__))
        else:  # custom object
            if isinstance(klass, type):
                return klass(**kwargs)
            else:  # object
                return klass

    @property
    def version(self):
        if hasattr(self, CachedClient.version_attr):
            return self._get_version()
        setattr(self, CachedClient.version_attr, CachedVersion(self))
        return self._get_version()

    @property
    def namespace(self):
        return CONFIG.cache.get('namespace', '#')

    def versioned_key(self, key, **opts):
        self.version.versioned_key(key, self.namespace)

    def fetch(self, key, miss_callback=None, **opts):
        pass

    def store(self, key, data, **opts):
        pass

    def delete(self, key, **opts):
        pass

    def exists(self, key, **opts):
        pass

    def clear(self):
        pass

    def read_only(self):
        return False

    def _get_version(self):
        return getattr(self, CachedClient.version_attr, None)
