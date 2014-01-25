import redisdl
import unittest
import json
import os.path
from . import util

class ModuleTest(unittest.TestCase):
    def setUp(self):
        import redis
        self.r = redis.Redis()
        for key in self.r.keys('*'):
            self.r.delete(key)

    def test_roundtrip(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dump.json')
        with open(path) as f:
            dump = f.read()

        redisdl.loads(dump)

        redump = redisdl.dumps()

        expected = json.loads(dump)
        actual = json.loads(redump)

        self.assertEqual(expected, actual)

    def test_dump_string_value(self):
        self.r.set('key', 'value')
        dump = redisdl.dumps()
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': 'value'}}
        self.assertEqual(expected, actual)

    def test_dump_unicode_value(self):
        self.r.set('key', u"\u041c\u043e\u0441\u043a\u0432\u0430")
        dump = redisdl.dumps()
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': u"\u041c\u043e\u0441\u043a\u0432\u0430"}}
        self.assertEqual(expected, actual)

    def test_load_string_value(self):
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        redisdl.loads(dump)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_unicode_value(self):
        dump = '{"key":{"type":"string","value":"\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430"}}'
        redisdl.loads(dump)
        value = self.r.get('key')
        self.assertEqual(util.b('\xd0\x9c\xd0\xbe\xd1\x81\xd0\xba\xd0\xb2\xd0\xb0'), value)
