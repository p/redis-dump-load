import nose.plugins.attrib
import redisdl
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import time as _time
import json
import os.path
from . import util
if redisdl.py3:
    from io import StringIO, BytesIO
else:
    try:
        from io import StringIO, BytesIO
    except ImportError:
        from StringIO import StringIO, StringIO as BytesIO


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

    def test_roundtrip_pretty(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dump.json')
        with open(path) as f:
            dump = f.read()

        redisdl.loads(dump)

        redump = redisdl.dumps(pretty=True)

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

    def test_load_stringio_str(self):
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(dump)
        redisdl.load(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_stringio_bytes(self):
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = BytesIO(dump.encode('ascii'))
        redisdl.load(io)
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

        @util.override_default_streaming_backend('ijson-yajl2')
        @util.requires_ijson
        @nose.plugins.attrib.attr('yajl2')
        def test_load_bytesio_yajl2_backend_bytes(self):
            self.assertTrue(redisdl.have_streaming_load)

            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = BytesIO(dump.encode('utf-8'))
            redisdl.load(io)
            value = self.r.get('key')
            self.assertEqual('hello, world', value.decode('ascii'))

        @util.override_default_streaming_backend('ijson-yajl2')
        @util.requires_ijson
        @nose.plugins.attrib.attr('yajl2')
        def test_load_bytesio_yajl2_backend_str(self):
            self.assertTrue(redisdl.have_streaming_load)

            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = StringIO(dump)
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

        start_time = _time.time()
        dump = redisdl.dumps(keys='a')
        end_time = _time.time()
        actual = json.loads(dump)

        self.assertGreater(actual['a']['ttl'], 0)
        self.assertLessEqual(actual['a']['ttl'], 3600)
        self.assertGreaterEqual(actual['a']['expireat'], int(start_time)+3600)
        self.assertLessEqual(actual['a']['expireat'], int(end_time)+1+3600)

    def test_ttl_loads(self):
        self.r.delete('b')
        dump = '''{"b":{"type":"string","value":"bbb","ttl":3600}}'''
        io = StringIO(dump)
        redisdl.load_lump(io)

        ttl = self.r.ttl('b')

        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 3600)

    def test_expireat_loads(self):
        self.r.delete('b')
        dump = '''{"b":{"type":"string","value":"bbb","expireat":_time.time() + 3600}}'''
        io = StringIO(dump)
        redisdl.load_lump(io)

        ttl = self.r.ttl('b')

        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 3600)

    def test_expireat_loads(self):
        self.r.delete('b')
        dump = '''{"b":{"type":"string","value":"bbb","expireat":%d}}''' % (
            _time.time() + 3600)
        io = StringIO(dump)
        redisdl.load_lump(io)

        ttl = self.r.ttl('b')

        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 3600)

    def test_no_ttl_dumps(self):
        self.r.set('a', 'aaa')

        dump = redisdl.dumps(keys='a')
        actual = json.loads(dump)

        self.assertTrue('ttl' not in actual['a'])
        self.assertTrue('expireat' not in actual['a'])

    @util.min_redis(2, 6)
    def test_ttl_precision(self):
        self.r.set('a', 'aaa')
        self.r.pexpire('a', 3600500)

        start_time = _time.time()
        dump = redisdl.dumps(keys='a')
        end_time = _time.time()
        actual = json.loads(dump)

        ttl = actual['a']['ttl']
        assert int((ttl - int(ttl)) * 1000) > 0

    def test_load_ttl_preference(self):
        dump = '{"key":{"type":"string","value":"hello, world","ttl":3600,"expireat":1472654445.3598034}}'
        redisdl.loads(dump)
        ttl = self.r.ttl('key')
        self.assertLess(ttl, 3601)

    def test_load_expireat_preference(self):
        dump = '{"key":{"type":"string","value":"hello, world","ttl":3600,"expireat":1472654445.3598034}}'
        redisdl.loads(dump, use_expireat=True)
        ttl = self.r.ttl('key')
        self.assertGreater(ttl, 36000)
