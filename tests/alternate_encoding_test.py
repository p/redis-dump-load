import redisdl
import unittest
import json
import os.path
from . import util

class RedisdlTest(unittest.TestCase):
    def setUp(self):
        import redis
        self.r = redis.Redis(charset='latin1')
        for key in self.r.keys('*'):
            self.r.delete(key)

    def test_dump_unicode_value(self):
        self.r.set('key', util.b('\xa9'))
        dump = redisdl.dumps(encoding='latin1')
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': util.u("\u00a9")}}
        self.assertEqual(expected, actual)

    def test_load_unicode_value(self):
        dump = '{"key":{"type":"string","value":"\\u00a9"}}'
        redisdl.loads(dump, encoding='latin1')
        value = self.r.get('key')
        self.assertEqual(util.b('\xa9'), value)
