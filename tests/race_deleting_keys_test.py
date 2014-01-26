import nose.plugins.attrib
import time as _time
import subprocess
import sys
import redisdl
import unittest
import json
import os.path
from . import util
from . import big_data

@nose.plugins.attrib.attr('slow')
class RaceDeletingKeysTest(unittest.TestCase):
    def setUp(self):
        import redis
        self.r = redis.Redis()
        for key in self.r.keys('*'):
            self.r.delete(key)

    def test_delete_race(self):
        bd = big_data.BigData(self.r)
        count = bd.determine_key_count()
        # data is already inserted

        big_data_path = os.path.join(os.path.dirname(__file__), 'big_data.py')
        p = subprocess.Popen(
            [sys.executable, big_data_path, 'delete', str(count)],
            stdout=subprocess.PIPE,
        )

        _time.sleep(1)
        start = _time.time()
        dump = redisdl.dumps()
        finish = _time.time()

        out, err = p.communicate()
        delete_start, delete_finish = [int(time) for time in out.split(' ')]

        assert delete_start < start
        assert finish > start + 5
        assert delete_finish > start + 5
