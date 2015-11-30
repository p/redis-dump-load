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

try:
    import ijson as ijson_root
    have_streaming_load = True
except ImportError:
    have_streaming_load = False


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

    def test_load_stringio_python_backend_global(self):
        if have_streaming_load:
            self.assertTrue(redisdl.have_streaming_load)
        redisdl.streaming_backend = 'python'
        
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(unicode(dump))
        redisdl.load(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_stringio_python_backend_local(self):
        if have_streaming_load:
            self.assertTrue(redisdl.have_streaming_load)
        
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(unicode(dump))
        redisdl.load(io, streaming_backend='python')
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_stringio_no_backend(self):
        if have_streaming_load:
            self.assertTrue(redisdl.have_streaming_load)
        redisdl.streaming_backend = None
        
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(unicode(dump))
        redisdl.load(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))

    def test_load_stringio_lump(self):
        dump = '{"key":{"type":"string","value":"hello, world"}}'
        io = StringIO(unicode(dump))
        redisdl.load_lump(io)
        value = self.r.get('key')
        self.assertEqual('hello, world', value.decode('ascii'))
    
    if redisdl.py3:
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
        @nose.plugins.attrib.attr('yajl2')
        def test_load_bytesio_yajl2_backend(self):
            self.assertTrue(redisdl.have_streaming_load)
            redisdl.streaming_backend = 'yajl2'
            
            dump = '{"key":{"type":"string","value":"hello, world"}}'
            io = BytesIO(dump.encode('utf-8'))
            redisdl.load(io)
            value = self.r.get('key')
            self.assertEqual('hello, world', value.decode('ascii'))
