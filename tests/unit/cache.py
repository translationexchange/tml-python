import unittest
import os
import time
from tml.cache import CacheVersion, CachedClient
from tml.cache_adapters import FileAdapter
from tml.cache_adapters.test_utils import check_alive
from tml.cache_adapters.memcached import PyLibMCCacheAdapter, DefaultMemcachedAdapter
from tml import configure
from .common import override_config, FIXTURES_PATH


class MockCachedClient(CachedClient):

    cache = {}

    def store(self, key, data, **opts):
        self.cache[key] = data

    def fetch(self, key, miss_callback=None, **opts):
        val = self.cache.get(key, None)
        if not val:
            val = self.cache[key] = miss_callback(key)
        return val

class DumbCachedClient(object):
    cache = {}
    def store(self, key, data, **opts):
        self.cache[key] = data

    def fetch(self, key):
        return self.cache[key]


class CacheVersionTest(unittest.TestCase):

    def setUp(self):
        configure()
        self.cache = MockCachedClient()
        self.test_version = "123-dummy"

    def test_init(self):
        version = CacheVersion(self.cache)
        self.assertIsInstance(version.cache, CachedClient, 'cache attr')
        version.set(self.test_version)
        self.assertEquals(version.version, self.test_version, 'version set')
        version.reset()
        self.assertEquals(version.version, None, 'version reset')

    def test_manipul(self):
        version = CacheVersion(self.cache)
        version.store(self.test_version)
        version_obj = version.fetch()
        self.assertTrue('t' in version_obj and 'version' in version_obj)
        self.assertEquals(version_obj['version'], self.test_version, "version fetch")
        with override_config(version_check_interval=-1):
            version_obj = version.fetch()
            self.assertEquals(version_obj['version'], 'undefined')
            self.assertTrue(version.is_undefined())
            self.assertTrue(version.is_invalid())
        version.store('new-ver')
        self.assertEquals(version.version, 'new-ver', 'stored')
        self.assertTrue(version.is_defined(), 'defined')
        self.assertTrue(version.is_valid())
        version.set(0)
        self.assertTrue(version.is_defined(), 'defined if 0')
        self.assertTrue(version.is_invalid(), '0 is not valid')



class CacheTest(unittest.TestCase):

    def setUp(self):
        self.snapshot_path = FIXTURES_PATH
        self.version = '20160218065921'

    def test_init_adapter(self):
        path = 'tests.unit.cache.DumbCachedClient'
        with override_config(cache={'enabled': True}):
            cache = CachedClient.instance(adapter=path)
            self.assertTrue(isinstance(cache, CachedClient))
            cache.store('foo', 'bar')
            self.assertEquals(cache.fetch('foo'), 'bar', 'work as adapter')
            self.assertTrue(hasattr(cache, 'versioned_key'), 'has inhereted methods')

    def test_file_adapter(self):
        with override_config(cache={'enabled': True}):
            cache = CachedClient.instance(adapter=FileAdapter)
            self.assertIsInstance(cache, CachedClient)
            self.assertEquals(cache.cache_name, 'file')

        with override_config(cache={'enabled': True, 'path': self.snapshot_path, 'version': self.version}):
            cache = CachedClient.instance(adapter=FileAdapter)
            self.assertEquals(cache.get_cache_path(), os.path.join(self.snapshot_path, self.version))
            self.assertEquals(cache.file_path('application'), os.path.join(self.snapshot_path, self.version, 'application.json'))
            app_data = cache.fetch('application')
            self.assertEquals(app_data['key'], 'ca77401b70d5efb91db42f15091a21a68e032ee20e93cd3539ce72b7b810fa1a')
            app_data = cache.fetch('application')

    def test_memcache_init(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'namespace': 'tml-2', 'ttl': 3600}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, DefaultMemcachedAdapter, 'proper factory build')
            self.assertEquals(cache.default_namespace, 'tml-2')
            self.assertEquals(cache.default_timeout, 3600)

        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'backend': 'pylibmc', 'host': '127.0.0.1', 'namespace': 'tml-3', 'ttl': 1200}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, PyLibMCCacheAdapter, 'proper factory build')
            self.assertEquals(cache.default_namespace, 'tml-3')
            self.assertEquals(cache.default_timeout, 1200)


    def test_memcache_funct(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'namespace': 'tml-test'}):
            cache = CachedClient.instance()
            check_alive(cache)
            self._test_memcache_func(cache)
            self._test_versioning(cache)

    def test_pylibmc_funct(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'backend': 'pylibmc', 'host': '127.0.0.1', 'namespace': 'tml-test'}):
            cache = CachedClient.instance()
            check_alive(cache)
            self._test_memcache_func(cache)
            self._test_versioning(cache)

    def _test_memcache_func(self, cache):
        self.assertEquals(cache.store('foo', 'bar'), 'bar', 'dummy store')
        self.assertEquals(cache.fetch('foo'), 'bar', 'dummy fetch')
        self.assertEquals(cache.delete('foo'), 'foo', 'dummy delete')
        self.assertEquals(cache.fetch('foo'), None, 'dummy check delete')
        self.assertEquals(cache.store('foo', {'a': 'b'}), {'a': 'b'}, 'json store')
        self.assertEquals(cache.fetch('foo'), {'a': 'b'}, 'json fetch')
        cache.delete('foo')
        cache.store('foo', 'new_bar', opts=dict(timeout=1))
        self.assertEquals(cache.fetch('foo'), 'new_bar', 'timeout')
        time.sleep(1)
        self.assertEquals(cache.fetch('foo'), None, 'timeout works')

    def _test_versioning(self, cache):
        cache.delete('a')
        cache.store_version('1312321')
        cache.store('a', 'b')
        self.assertEquals(cache.fetch('a'), 'b', 'upgrade version')
        cache.upgrade_version()
        self.assertEquals(cache.fetch('a'), None, 'upgrade version works')

if __name__ == '__main__':
    unittest.main()
