import redisdl
import unittest
import json
import os.path

class RedisdlTest(unittest.TestCase):
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
