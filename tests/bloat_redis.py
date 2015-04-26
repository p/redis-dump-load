import redis

client = redis.Redis()

for i in range(100000):
    client.set('testkey%d' % i, 'testvalue%d' % i)
