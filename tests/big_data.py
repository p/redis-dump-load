import time as _time

class BigData(object):
    def __init__(self, r):
        self.r = r

    # overwrites the keys, doubling the time it takes to figure out the answer
    def determine_key_count(self):
        for p in range(14, 19):
            start = _time.time()
            self.insert(2**p)
            elapsed = _time.time() - start
            if elapsed > 10:
                return 2**p
        return 2**19

    def insert(self, count=100000):
        for i in range(count):
            self.r.set('key-%d' % i, 'value-%d' % i)

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
