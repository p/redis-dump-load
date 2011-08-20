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
        yield key, type, value

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
