import pytest
import os
import time
import unittest
from tml.config import CONFIG
from tml.cache import CacheVersion, CachedClient
from tml.cache_adapters import file as FileAdapter
from tml.cache_adapters.test_utils import check_alive
from tml.cache_adapters.memcached import PyLibMCCacheAdapter, DefaultMemcachedAdapter, BaseMemcachedAdapter
from tml.cache_adapters.rediscache import BaseRedisAdapter, DefaultRedisAdapter
from tml import configure
from tests.common import override_config, FIXTURES_PATH
from .settings import TML

MEMCACHE_CONNECTION = ['127.0.0.1:11211']


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

class TestCacheVersion(unittest.TestCase):

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
        cur_version = version.fetch()
        self.assertEquals(cur_version, self.test_version, "version fetch")
        with override_config(version_check_interval=-1):
            cur_version = version.fetch()
            self.assertEquals(cur_version, 'undefined')
            self.assertTrue(version.is_undefined())
            self.assertTrue(version.is_invalid())
        version.store('new-ver')
        self.assertEquals(version.version, 'new-ver', 'stored')
        self.assertTrue(version.is_defined(), 'defined')
        self.assertTrue(version.is_valid())
        version.set(0)
        self.assertTrue(version.is_defined(), 'defined if 0')
        self.assertTrue(version.is_invalid(), '0 is not valid')


@pytest.mark.usefixtures("memcached")
class TestCache(unittest.TestCase):

    def test_init_adapter(self):
        path = 'tests.integration.cache.DumbCachedClient'
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

        with override_config(cache={'enabled': True, 'path': TML['cache']['path'], 'version': TML['cache']['version']}):
            cache = CachedClient.instance(adapter=FileAdapter)
            self.assertEquals(cache.get_cache_path(), os.path.join(TML['cache']['path'], TML['cache']['version']))
            self.assertEquals(cache.file_path('application'), os.path.join(TML['cache']['path'], TML['cache']['version'], 'application.json'))
            app_data = cache.fetch('application')
            self.assertEquals(app_data['key'], TML['application']['key'])
            app_data = cache.fetch('application')

    def test_memcache_init(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'ttl': 3600, 'namespace': ''}):
            cache = CachedClient.instance()
            self.assertEquals(cache.namespace, CONFIG.application_key()[:5], 'namespace set first 5 symbols of key')

        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'ttl': 3600, 'namespace': ''}, application={'access_token': 'foobar'}):
            cache = CachedClient.instance()
            self.assertEquals(cache.namespace, CONFIG.access_token()[:5], 'namespace set first 5 symbols of token')


        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'namespace': 'tml-2', 'ttl': 3600}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, BaseMemcachedAdapter, 'proper factory build')
            self.assertEquals(cache.default_timeout, 3600)
            self.assertEquals(cache.namespace, 'tml-2', 'namespace set')
            cache._drop_it()

        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'backend': 'pylibmc', 'host': '127.0.0.1', 'namespace': 'tml-3', 'ttl': 1200}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, BaseMemcachedAdapter, 'proper factory build')
            self.assertEquals(cache.default_timeout, 1200)
            cache._drop_it()


    def test_memcache_funct(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'host': '127.0.0.1', 'namespace': 'tml-test'}):
            cache = CachedClient.instance()
            check_alive(cache)
            self._test_memcache_func(cache)
            self._test_versioning(cache)
            cache._drop_it()

    def test_pylibmc_funct(self):
        with override_config(cache={'enabled': True, 'adapter': 'memcached', 'backend': 'pylibmc', 'host': '127.0.0.1', 'namespace': 'tml-test'}):
            cache = CachedClient.instance()
            check_alive(cache)
            self._test_memcache_func(cache)
            self._test_versioning(cache)
            cache._drop_it()

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


class TestRedisCache(unittest.TestCase):
    def test_redis_init(self):
        with override_config(cache={'enabled': True, 'adapter': 'rediscache', 'host': '127.0.0.1:6379', 'namespace': 'tml-2', 'ttl': 3600}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, BaseRedisAdapter, 'proper factory build')
            self.assertEquals(cache.default_timeout, 3600)
            self.assertEquals(cache.namespace, 'tml-2', 'namespace set')
            cache._drop_it()

        with override_config(cache={'enabled': True, 'adapter': 'rediscache', 'backend': 'default', 'host': '127.0.0.1:6379', 'namespace': 'tml-3', 'ttl': 1200}):
            cache = CachedClient.instance()
            self.assertIsInstance(cache, BaseRedisAdapter, 'proper factory build')
            self.assertEquals(cache.default_timeout, 1200)
            cache._drop_it()

        with override_config(cache={'enabled': True, 'adapter': 'rediscache', 'backend': 'default', 'host': '127.0.0.1:6379', 'options': {'pool': True, 'max_connections': 2}}):
            import redis
            cache = CachedClient.instance()
            self.assertIsInstance(cache._cache, redis.ConnectionPool)
            self.assertEquals(cache._cache.max_connections, 2)
            cache._drop_it()

    def test_redis_func(self):
        with override_config(cache={'enabled': True, 'adapter': 'rediscache', 'backend': 'default', 'host': '127.0.0.1:6379', 'namespace': 'tml-test'}):
            cache = CachedClient.instance()
            check_alive(cache)
            self.assertEquals(cache.store('foo', ['bar']), ['bar'], 'dummy store')
            self.assertEquals(cache.fetch('foo'), ['bar'], 'dummy fetch')
            self.assertEquals(cache.delete('foo'), 'foo', 'dummy delete')
            self.assertEquals(cache.fetch('foo'), None, 'dummy check delete')
            self.assertEquals(cache.store('foo', {'a': 'b'}), {'a': 'b'}, 'json store')
            self.assertEquals(cache.fetch('foo'), {'a': 'b'}, 'json fetch')
            cache.delete('foo')
            cache.store('foo', 'new_bar', opts=dict(timeout=1))
            self.assertEquals(cache.fetch('foo'), 'new_bar', 'timeout')
            time.sleep(1)
            self.assertEquals(cache.fetch('foo'), None, 'timeout works')
