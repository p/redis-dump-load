import json
import redis

def dumps(host='localhost', port=6379, db=0):
    r = redis.Redis(host=host, port=port, db=db)
    encoder = json.JSONEncoder(separators=(',', ':'))
    table = {}
    for key, type, value in _reader(r):
        table[key] = {'type': type, 'value': value}
    return encoder.encode(table)

def dump(fp, host='localhost', port=6379, db=0):
    r = redis.Redis(host=host, port=port, db=db)
    encoder = json.JSONEncoder(separators=(',', ':'))
    fp.write('{')
    first = True
    for key, type, value in _reader(r):
        key = encoder.encode(key)
        type = encoder.encode(type)
        value = encoder.encode(value)
        item = '%s:{"type":%s,"value":%s}' % (key, type, value)
        if first:
            first = False
        else:
            fp.write(',')
        fp.write(item)
    fp.write('}')

def _reader(r):
    for key in r.keys():
        type = r.type(key)
        if type == 'string':
            value = r.get(key)
        elif type == 'list':
            value = r.lrange(key, 0, -1)
        elif type == 'set':
            value = list(r.smembers(key))
        elif type == 'zset':
            value = r.zrange(key, 0, -1, False, True)
        elif type == 'hash':
            value = r.hgetall(key)
        else:
            raise UnknownTypeError("Unknown key type: %s" % type)
        yield key, type, value

def loads(s, host='localhost', port=6379, db=0):
    r = redis.Redis(host=host, port=port, db=db)
    table = json.loads(s)
    for key in table:
        item = table[key]
        type = item['type']
        value = item['value']
        _writer(r, key, type, value)

def load(fp, host='localhost', port=6379, db=0):
    s = fp.read()
    loads(s, host, port, db)

def _writer(r, key, type, value):
    r.delete(key)
    if type == 'string':
        r.set(key, value)
    elif type == 'list':
        for element in value:
            r.lpush(key, element)
    elif type == 'set':
        for element in value:
            r.sadd(key, element)
    elif type == 'zset':
        for element, score in value:
            r.zadd(key, element, score)
    elif type == 'hash':
        r.hmset(key, value)
    else:
        raise UnknownTypeError("Unknown key type: %s" % type)

if __name__ == '__main__':
    import optparse
    import sys
    
    parser = optparse.OptionParser()
    parser.add_option('-H', '--host', help='connect to HOST (default localhost)')
    parser.add_option('-p', '--port', help='connect to PORT (default 6379)')
    parser.add_option('-s', '--socket', help='connect to SOCKET')
    parser.add_option('-d', '--db', help='dump DATABASE (0-N, default 0)')
    parser.add_option('-o', '--output', help='write to OUTPUT instead of stdout')
    options, args = parser.parse_args()
    
    if options.output:
        output = open(options.output, 'w')
    else:
        output = sys.stdout
    
    args = {}
    if options.host:
        args['host'] = options.host
    if options.port:
        args['port'] = int(options.port)
    if options.db:
        args['db'] = int(options.db)
    dump(output, **args)
    
    if options.output:
        output.close()
