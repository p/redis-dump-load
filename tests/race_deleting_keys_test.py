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

key_count = None

@nose.plugins.attrib.attr('slow')
class RaceDeletingKeysTest(unittest.TestCase):
    def setUp(self):
        import redis
        self.r = redis.Redis()
        for key in self.r.keys('*'):
            self.r.delete(key)

        global key_count
        if key_count is None:
            bg = big_data.BigData(self.r)
            key_count = bg.determine_key_count()

        self.data_process = None

    def tearDown(self):
        if self.data_process is not None:
            if self.data_process.poll() is None:
                self.data_process.communicate()

    def test_delete_race_strings(self):
        self.check_delete_race('strings')

    def test_delete_race_lists(self):
        self.check_delete_race('lists')

    def test_delete_race_sets(self):
        self.check_delete_race('sets')

    def test_delete_race_zsets(self):
        self.check_delete_race('zsets')

    def test_delete_race_hashes(self):
        self.check_delete_race('hashes')

    def check_delete_race(self, suffix):
        bd = big_data.BigData(self.r)
        getattr(bd, 'insert_%s' % suffix)(key_count)

        big_data_path = os.path.join(os.path.dirname(__file__), 'big_data.py')
        self.data_process = subprocess.Popen(
            [sys.executable, big_data_path, 'delete', str(key_count)],
            stdout=subprocess.PIPE,
        )

        _time.sleep(1)
        start = _time.time()
        dump = redisdl.dumps()
        finish = _time.time()

        out, err = self.data_process.communicate()
        delete_start, delete_finish = [int(time) for time in out.decode().split(' ')]

        assert delete_start < start
        assert finish > start + 5
        assert delete_finish > start + 5
