#!/usr/bin/env python

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

def loads(s, host='localhost', port=6379, db=0, empty=False):
    r = redis.Redis(host=host, port=port, db=db)
    if empty:
        for key in r.keys():
            r.delete(key)
    table = json.loads(s)
    for key in table:
        item = table[key]
        type = item['type']
        value = item['value']
        _writer(r, key, type, value)

def load(fp, host='localhost', port=6379, db=0, empty=False):
    s = fp.read()
    loads(s, host, port, db, empty)

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
    import os.path
    import re
    import sys
    
    DUMP = 1
    LOAD = 2
    
    def options_to_kwargs(options):
        args = {}
        if options.host:
            args['host'] = options.host
        if options.port:
            args['port'] = int(options.port)
        if options.db:
            args['db'] = int(options.db)
        # load only
        if options.empty:
            args['empty'] = True
        return args
    
    def do_dump(options):
        if options.output:
            output = open(options.output, 'w')
        else:
            output = sys.stdout
        
        kwargs = options_to_kwargs(options)
        dump(output, **kwargs)
        
        if options.output:
            output.close()
    
    def do_load(options, args):
        if len(args) > 0:
            input = open(args[0], 'r')
        else:
            input = sys.stdin
        
        kwargs = options_to_kwargs(options)
        load(input, **kwargs)
        
        if len(args) > 0:
            input.close()
    
    if re.search(r'load(?:$|\.)', os.path.basename(sys.argv[0])):
        action = LOAD
    else:
        action = DUMP
    
    if action == LOAD:
        usage = "Usage: %prog [options] [FILE]"
        usage += "\n\nLoad data from FILE (which must be a JSON dump previously created"
        usage += "\nby redisdl) into specified or default redis."
        usage += "\n\nIf FILE is omitted standard input is read."
    else:
        usage = "Usage: %prog [options]"
        usage += "\n\nDump data from specified or default redis."
        usage += "\n\nIf no output file is specified, dump to standard output."
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-H', '--host', help='connect to HOST (default localhost)')
    parser.add_option('-p', '--port', help='connect to PORT (default 6379)')
    parser.add_option('-s', '--socket', help='connect to SOCKET')
    if action == DUMP:
        parser.add_option('-d', '--db', help='dump DATABASE (0-N, default 0)')
        parser.add_option('-o', '--output', help='write to OUTPUT instead of stdout')
    else:
        parser.add_option('-d', '--db', help='import into DATABASE (0-N, default 0)')
        parser.add_option('-e', '--empty', help='delete all keys in destination db prior to loading')
    options, args = parser.parse_args()
    
    if action == DUMP:
        if len(args) > 0:
            parser.print_help()
            exit(4)
        do_dump(options)
    else:
        if len(args) > 1:
            parser.print_help()
            exit(4)
        do_load(options, args)
