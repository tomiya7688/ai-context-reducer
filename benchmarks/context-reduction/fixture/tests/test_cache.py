import unittest
from src.cache import Cache

class CacheTests(unittest.TestCase):
    def test_put_and_get(self):
        cache = Cache()
        cache.put("key", "value")
        self.assertEqual("value", cache.get("key"))

if __name__ == "__main__":
    unittest.main()
