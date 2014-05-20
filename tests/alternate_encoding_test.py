import redis
import redisdl
import unittest
import json
import os.path
from . import util

class RedisdlTest(unittest.TestCase):
    def setUp(self):
        self.r = redis.Redis()
        for key in self.r.keys('*'):
            self.r.delete(key)

    def test_dump_latin1(self):
        self.r = redis.Redis(charset='latin1')
        self.r.set('key', util.b('\xa9'))
        dump = redisdl.dumps(encoding='latin1')
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': util.u("\u00a9")}}
        self.assertEqual(expected, actual)

    def test_load_latin1(self):
        self.r = redis.Redis(charset='latin1')
        dump = '{"key":{"type":"string","value":"\\u00a9"}}'
        redisdl.loads(dump, encoding='latin1')
        value = self.r.get('key')
        self.assertEqual(util.b('\xa9'), value)

    # utf-16 is not a superset of ascii
    # this tests that key type is correctly retrieved
    def test_dump_utf16(self):
        self.r = redis.Redis(charset='utf-16')
        self.r.set(util.u('key'), util.b('\xff\xfeh\x00e\x00l\x00l\x00o\x00'))
        dump = redisdl.dumps(encoding='utf-16')
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': util.u("hello")}}
        self.assertEqual(expected, actual)

    def test_load_utf16(self):
        self.r = redis.Redis(charset='utf-16')
        dump = '{"key":{"type":"string","value":"hello"}}'
        redisdl.loads(dump, encoding='utf-16')
        value = self.r.get(util.u('key'))
        self.assertEqual(util.b('\xff\xfeh\x00e\x00l\x00l\x00o\x00'), value)
    
    def test_empty_with_mixed_encodings(self):
        r = redis.Redis(charset='utf-16')
        r.set(util.u('key'), util.b('\xff\xfeh\x00e\x00l\x00l\x00o\x00'))
        r = redis.Redis(charset='utf-8')
        self.assertEqual(1, len(r.keys('*')))
        try:
            r.keys('*')[0].decode('utf-8')
        except UnicodeDecodeError:
            pass
        else:
            self.fail('Expected decoding in utf-8 to fail')
        redisdl._empty(r)
        self.assertEqual(0, len(r.keys('*')))
