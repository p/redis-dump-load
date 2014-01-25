import redisdl
import subprocess
import unittest
import json
import os.path
from . import util

class ProgramTest(unittest.TestCase):
    def setUp(self):
        import redis
        self.r = redis.Redis()
        for key in self.r.keys('*'):
            self.r.delete(key)

        self.program = os.path.join(os.path.dirname(__file__), '..', 'redisdl.py')

    def test_dump(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dump.json')
        with open(path) as f:
            dump = f.read()

        redisdl.loads(dump)

        redump = subprocess.check_output([self.program])

        expected = json.loads(dump)
        actual = json.loads(redump)

        self.assertEqual(expected, actual)

    def test_load(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dump.json')
        with open(path) as f:
            dump = f.read()

        subprocess.check_call([self.program, '-l', path])

        redump = redisdl.dumps()

        expected = json.loads(dump)
        actual = json.loads(redump)

        self.assertEqual(expected, actual)
