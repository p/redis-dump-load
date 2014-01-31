#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json
import redis
import sys
import functools

py3 = sys.version_info[0] == 3

if py3:
    base_exception_class = Exception
else:
    base_exception_class = StandardError

class UnknownTypeError(base_exception_class):
    pass

class ConcurrentModificationError(base_exception_class):
    pass

# internal exceptions

class KeyDeletedError(base_exception_class):
    pass

class KeyTypeChangedError(base_exception_class):
    pass

def client(host='localhost', port=6379, password=None, db=0,
                 unix_socket_path=None, encoding='utf-8'):
    if unix_socket_path is not None:
        r = redis.Redis(unix_socket_path=unix_socket_path,
                        password=password,
                        db=db,
                        charset=encoding)
    else:
        r = redis.Redis(host=host,
                        port=port,
                        password=password,
                        db=db,
                        charset=encoding)
    return r

def dumps(host='localhost', port=6379, password=None, db=0, pretty=False,
          unix_socket_path=None, encoding='utf-8'):
    r = client(host=host, port=port, password=password, db=db,
               unix_socket_path=unix_socket_path, encoding=encoding)
    kwargs = {}
    if not pretty:
        kwargs['separators'] = (',', ':')
    else:
        kwargs['indent'] = 2
        kwargs['sort_keys'] = True
    encoder = json.JSONEncoder(**kwargs)
    table = {}
    for key, type, value in _reader(r, pretty, encoding):
        table[key] = {'type': type, 'value': value}
    return encoder.encode(table)

def dump(fp, host='localhost', port=6379, password=None, db=0, pretty=False,
         unix_socket_path=None, encoding='utf-8'):
    if pretty:
        # hack to avoid implementing pretty printing
        fp.write(dumps(host=host, port=port, password=password, db=db,
            pretty=pretty, encoding=encoding))
        return

    r = client(host=host, port=port, password=password, db=db,
               unix_socket_path=unix_socket_path, encoding=encoding)
    kwargs = {}
    if not pretty:
        kwargs['separators'] = (',', ':')
    else:
        kwargs['indent'] = 2
        kwargs['sort_keys'] = True
    encoder = json.JSONEncoder(**kwargs)
    fp.write('{')
    first = True
    for key, type, value in _reader(r, pretty, encoding):
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

class StringReader(object):
    @staticmethod
    def send_command(p, key):
        p.get(key)

    @staticmethod
    def handle_response(response, pretty, encoding):
        # if key does not exist, get will return None;
        # however, our type check requires that the key exists
        return response.decode(encoding)

class ListReader(object):
    @staticmethod
    def send_command(p, key):
        p.lrange(key, 0, -1)

    @staticmethod
    def handle_response(response, pretty, encoding):
        return [v.decode(encoding) for v in response]

class SetReader(object):
    @staticmethod
    def send_command(p, key):
        p.smembers(key)

    @staticmethod
    def handle_response(response, pretty, encoding):
        value = [v.decode(encoding) for v in response]
        if pretty:
            value.sort()
        return value

class ZsetReader(object):
    @staticmethod
    def send_command(p, key):
        p.zrange(key, 0, -1, False, True)

    @staticmethod
    def handle_response(response, pretty, encoding):
        return [(k.decode(encoding), score) for k, score in response]

class HashReader(object):
    @staticmethod
    def send_command(p, key):
        p.hgetall(key)

    @staticmethod
    def handle_response(response, pretty, encoding):
        value = {}
        for k in response:
            value[k.decode(encoding)] = response[k].decode(encoding)
        return value

readers = {
    'string': StringReader,
    'list': ListReader,
    'set': SetReader,
    'zset': ZsetReader,
    'hash': HashReader,
}

# note: key is a byte string
def _read_key(key, r, pretty, encoding):
    type = r.type(key).decode('ascii')
    if type == 'none':
        # key was deleted by a concurrent operation on the data store
        raise KeyDeletedError
    reader = readers.get(type)
    if reader is None:
        raise UnknownTypeError("Unknown key type: %s" % type)
    p = r.pipeline()
    p.watch(key)
    p.multi()
    p.type(key)
    reader.send_command(p, key)
    # might raise redis.WatchError
    results = p.execute()
    actual_type = results[0].decode('ascii')
    if actual_type != type:
        # type changed, retry
        raise KeyTypeChangedError
    value = reader.handle_response(results[1], pretty, encoding)
    return (type, value)

def _reader(r, pretty, encoding):
    for encoded_key in r.keys():
        key = encoded_key.decode(encoding)
        handled = False
        for i in range(10):
            try:
                type, value = _read_key(encoded_key, r, pretty, encoding)
                yield key, type, value
                handled = True
                break
            except KeyDeletedError:
                # do not dump the key
                handled = True
                break
            except redis.WatchError:
                # same logic as key type changed
                pass
            except KeyTypeChangedError:
                # retry reading type again
                pass
        if not handled:
            # ran out of retries
            raise ConcurrentModificationError('Key %s is being concurrently modified' % key)

def loads(s, host='localhost', port=6379, password=None, db=0, empty=False,
          unix_socket_path=None, encoding='utf-8'):
    r = client(host=host, port=port, password=password, db=db,
               unix_socket_path=unix_socket_path, encoding=encoding)
    if empty:
        for key in r.keys():
            r.delete(key)
    table = json.loads(s)
    counter = 0
    for key in table:
        # Create pipeline:
        if not counter:
            p = r.pipeline(transaction=False)
        item = table[key]
        type = item['type']
        value = item['value']
        _writer(p, key, type, value)
        # Increase counter until 10 000...
        counter = (counter + 1) % 10000
        # ... then execute:
        if not counter:
            p.execute()
    if counter:
        # Finally, execute again:
        p.execute()

def load(fp, host='localhost', port=6379, password=None, db=0, empty=False,
         unix_socket_path=None, encoding='utf-8'):
    s = fp.read()
    loads(s, host, port, password, db, empty, unix_socket_path, encoding)

def _writer(r, key, type, value):
    r.delete(key)
    if type == 'string':
        r.set(key, value)
    elif type == 'list':
        for element in value:
            r.rpush(key, element)
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
        if options.socket:
            args['unix_socket_path'] = options.socket
        if options.password:
            args['password'] = options.password
        if options.db:
            args['db'] = int(options.db)
        if options.encoding:
            args['encoding'] = options.encoding
        # dump only
        if hasattr(options, 'pretty') and options.pretty:
            args['pretty'] = True
        # load only
        if hasattr(options, 'empty') and options.empty:
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

    script_name = os.path.basename(sys.argv[0])
    if re.search(r'load(?:$|\.)', script_name):
        action = help = LOAD
    elif re.search(r'dump(?:$|\.)', script_name):
        action = help = DUMP
    else:
        # default is dump, however if dump is specifically requested
        # we don't show help text for toggling between dumping and loading
        action = DUMP
        help = None

    if help == LOAD:
        usage = "Usage: %prog [options] [FILE]"
        usage += "\n\nLoad data from FILE (which must be a JSON dump previously created"
        usage += "\nby redisdl) into specified or default redis."
        usage += "\n\nIf FILE is omitted standard input is read."
    elif help == DUMP:
        usage = "Usage: %prog [options]"
        usage += "\n\nDump data from specified or default redis."
        usage += "\n\nIf no output file is specified, dump to standard output."
    else:
        usage = "Usage: %prog [options]"
        usage += "\n       %prog -l [options] [FILE]"
        usage += "\n\nDump data from redis or load data into redis."
        usage += "\n\nIf input or output file is specified, dump to standard output and load"
        usage += "\nfrom standard input."
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-H', '--host', help='connect to HOST (default localhost)')
    parser.add_option('-p', '--port', help='connect to PORT (default 6379)')
    parser.add_option('-s', '--socket', help='connect to SOCKET')
    parser.add_option('-w', '--password', help='connect with PASSWORD')
    if help == DUMP:
        parser.add_option('-d', '--db', help='dump DATABASE (0-N, default 0)')
        parser.add_option('-o', '--output', help='write to OUTPUT instead of stdout')
        parser.add_option('-y', '--pretty', help='Split output on multiple lines and indent it', action='store_true')
        parser.add_option('-E', '--encoding', help='set encoding to use while decoding data from redis', default='utf-8')
    elif help == LOAD:
        parser.add_option('-d', '--db', help='load into DATABASE (0-N, default 0)')
        parser.add_option('-e', '--empty', help='delete all keys in destination db prior to loading')
        parser.add_option('-E', '--encoding', help='set encoding to use while encoding data to redis', default='utf-8')
    else:
        parser.add_option('-l', '--load', help='load data into redis (default is to dump data from redis)', action='store_true')
        parser.add_option('-d', '--db', help='dump or load into DATABASE (0-N, default 0)')
        parser.add_option('-o', '--output', help='write to OUTPUT instead of stdout (dump mode only)')
        parser.add_option('-y', '--pretty', help='Split output on multiple lines and indent it (dump mode only)', action='store_true')
        parser.add_option('-e', '--empty', help='delete all keys in destination db prior to loading (load mode only)', action='store_true')
        parser.add_option('-E', '--encoding', help='set encoding to use while decoding data from redis', default='utf-8')
    options, args = parser.parse_args()

    if options.load:
        action = LOAD

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
