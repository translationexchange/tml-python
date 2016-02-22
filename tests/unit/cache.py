import unittest
from tml.cache import CacheVersion, CachedClient
from tml import configure
from .common import override_config


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

    def test_init_adapter(self):
        path = 'tests.unit.cache.DumbCachedClient'
        with override_config(cache={'enabled': True}):
            cache = CachedClient.instance(adapter=path)
            self.assertTrue(isinstance(cache, CachedClient))
            cache.store('foo', 'bar')
            self.assertEquals(cache.fetch('foo'), 'bar', 'work as adapter')
            self.assertTrue(hasattr(cache, 'versioned_key'), 'has inhereted methods')

if __name__ == '__main__':
    unittest.main()
