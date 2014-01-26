import time as _time

class BigData(object):
    def __init__(self, r):
        self.r = r

    # overwrites the keys, doubling the time it takes to figure out the answer.
    # we can also extrapolate the time after we have a meaningfully long
    # batch that is still shorter than target (say, 2 seconds)
    def determine_key_count(self):
        count = None
        for p in range(14, 19):
            start = _time.time()
            self.insert_strings(2**p)
            elapsed = _time.time() - start
            if elapsed > 10:
                count = 2**p
                break
        self.delete(2**p)
        if count is None:
            count = 2**19
        return count

    def insert_strings(self, count=100000):
        for i in range(count):
            self.r.set('key-%d' % i, 'value-%d' % i)

    def insert_lists(self, count=100000):
        for i in range(count):
            self.r.rpush('key-%d' % i, 'value-%d' % i)

    def insert_sets(self, count=100000):
        for i in range(count):
            self.r.sadd('key-%d' % i, 'value-%d' % i)

    def insert_zsets(self, count=100000):
        for i in range(count):
            self.r.zadd('key-%d' % i, 'value-%d' % i, 1)

    def insert_hashes(self, count=100000):
        for i in range(count):
            self.r.hset('key-%d' % i, 'hkey', 'value-%d' % i)

    def delete(self, count=100000):
        start = _time.time()
        for i in range(count):
            self.r.delete('key-%d' % i)
        finish = _time.time()
        print('%d %d' % (start, finish))

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'delete':
            import redis
            r = redis.Redis()
            if len(sys.argv) > 2:
                count = int(sys.argv[2])
            else:
                count = 100000
            BigData(r).delete(count)
