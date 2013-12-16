import redisdl
import unittest
import json
import os.path

class RedisdlTest(unittest.TestCase):
    def test_roundtrip(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dump.json')
        with open(path) as f:
            dump = f.read()
        
        redisdl.loads(dump)
        
        redump = redisdl.dumps()
        
        expected = json.loads(dump)
        actual = json.loads(redump)
        
        self.assertEqual(expected, actual)
