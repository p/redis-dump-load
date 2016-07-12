import nose.plugins.attrib
import redisdl
import unittest
import json
import os.path
from . import util
if redisdl.py3:
    from io import StringIO, BytesIO
else:
    from StringIO import StringIO


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
        self.r.set('key', util.u("\u041c\u043e\u0441\u043a\u0432\u0430"))
        dump = redisdl.dumps()
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': util.u("\u041c\u043e\u0441\u043a\u0432\u0430")}}
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

    @util.requires_ijson
    def test_load_stringio_python_backend_global(self):
        self.assertTrue(redisdl.have_streaming_load)
        redisdl.streaming_backend = 'python'

        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(dump)
        redisdl.load(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    @util.requires_ijson
    def test_load_stringio_python_backend_local(self):
        self.assertTrue(redisdl.have_streaming_load)

        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(dump)
        redisdl.load(io, streaming_backend='python')
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    @util.requires_ijson
    def test_load_stringio_no_backend(self):
        self.assertTrue(redisdl.have_streaming_load)
        redisdl.streaming_backend = None

        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(dump)
        redisdl.load(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_stringio_lump(self):
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(dump)
        redisdl.load_lump(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    if redisdl.py3:
        @util.requires_ijson
        def test_load_bytesio(self):
            self.assertTrue(redisdl.have_streaming_load)

            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = BytesIO(dump.encode('utf-8'))
            redisdl.load(io)
            value = self.r.get('key')
            self.assertEqual('hello, world', value.decode('ascii'))

        def test_load_bytesio_lump(self):
            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = BytesIO(dump.encode('utf-8'))
            redisdl.load_lump(io)
            value = self.r.get('key')
            self.assertEqual('hello, world', value.decode('ascii'))

        # yajl2 backend does not appear to be capable of loading StringIOs
        @util.requires_ijson
        @nose.plugins.attrib.attr('yajl2')
        def test_load_bytesio_yajl2_backend(self):
            self.assertTrue(redisdl.have_streaming_load)
            redisdl.streaming_backend = 'yajl2'

            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = BytesIO(dump.encode('utf-8'))
            redisdl.load(io)
            value = self.r.get('key')
            self.assertEqual('hello, world', value.decode('ascii'))

    def test_dump_specified_keys(self):
        self.r.set('key', 'value')
        self.r.set('ignore_key', 'value')
        dump = redisdl.dumps(keys='k*')
        actual = json.loads(dump)
        expected = {'key': {'type': 'string', 'value': 'value'}}
        self.assertEqual(expected, actual)

    def test_ttl_dumps(self):
        self.r.set('a', 'aaa')
        self.r.expire('a', 3600)

        dump = redisdl.dumps(keys='a')
        actual = json.loads(dump)

        self.assertGreater(actual['a']['ttl'], 0)
        self.assertLessEqual(actual['a']['ttl'], 3600)

    def test_ttl_loads(self):
        self.r.delete('b')
        dump = '''{"b":{"type":"string","value":"bbb","ttl":3600}}'''
        io = StringIO(dump)
        redisdl.load_lump(io)

        ttl = self.r.ttl('b')

        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 3600)

