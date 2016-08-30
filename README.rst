redis-dump-load
===============

.. image:: https://api.travis-ci.org/p/redis-dump-load.png
  :target: https://travis-ci.org/p/redis-dump-load

Dumps Redis data sets into a format suitable for long-term storage
(currently JSON) and loads data from such dump files back into Redis.

Features
--------

redis-dump-load:

- Supports all Redis data types;
- Dumps TTL and expiration times;
- Can load TTL OR original expiration time for expiring keys;
- Can create pretty/human-readable dumps (keys dumped in sorted order,
  output indented);
- Can stream data when dumping and loading;
- Can be used as a module in a larger program or as a standalone utility;
- Uses an output format compatible with redis-dump_.

Usage
-----

redis-dump-load may be used as a module and also as a command line tool.

Module Usage
^^^^^^^^^^^^

redis-dump-load exports a pickle_-like interface, namely ``load``,
``loads``, ``dump`` and ``dumps`` functions. For example::

    import redisdl

    json_text = redisdl.dumps()

    with open('path/to/dump.json', 'w') as f:
        # streams data
        redisdl.dump(f)

    json_text = '...'
    redisdl.loads(json_text)

    with open('path/to/dump.json') as f:
        # streams data if ijson or jsaone are installed
        redisdl.load(f)

See the streaming section below for more information about streaming.

Dump and load methods accept options as keyword arguments::

    json_text = redisdl.dumps(encoding='iso-8859-1', pretty=True)

The arguments should always be passed in as keywords, i.e, do not rely
on the order in which the parameters are currently listed.
Options take string values unless otherwise noted. The options are as follows:

- ``host``: host name or IP address for redis server
- ``port``: port number for redis server
- ``unix_socket_path``: connect to redis via a Unix socket instead of TCP/IP;
  specify the path to the socket
- ``password``: specify password to connect to redis
- ``db`` (integer): redis database to connect to
- ``encoding``: encoding to use for encoding or decoding the data, see
  Unicode section below
- ``pretty`` (boolean, dump only): produce a pretty-printed JSON which is
  easier to read; currently this makes ``dump`` load entire data set into
  memory rather than stream it
- ``keys`` (dump only): only dump keys matching specified pattern
- ``use_expireat`` (boolean, load only): use ``expireat`` in preference to ``ttl`` when loading expiring keys
- ``empty`` (boolean, load only): empty the redis data set before loading the
  data
- ``streaming_backend`` (string): streaming backend to use when loading via
  ``load`` method, if ijson_ or jsaone_ is installed and streaming is thus used

Command Line Usage
^^^^^^^^^^^^^^^^^^

``redisdl.py`` can be used as a command line tool as follows::

    # dump database 0
    ./redisdl.py > dump.json
    ./redisdl.py -o dump.json

    # load into database 0
    ./redisdl.py -l < dump.json
    ./redisdl.py -l dump.json

For convenience, ``redisdl.py`` can be hard or soft linked as follows::

    ln redisdl.py redis-dump
    ln redisdl.py redis-load

Now it can be used thusly::

    # dump database 0
    ./redis-dump > dump.json
    ./redis-dump -o dump.json

    # load into database 0
    ./redis-load < dump.json
    ./redis-load dump.json

Symlinks work as well. "load" in the executable name triggers the loading
mode, "dump" triggers the dumping mode, otherwise the default is to dump
and ``-l`` option switches into the loading mode.

All options supported by the module API are accepted when redisdl is invoked
as a command line tool. The command line options are:

- ``-h``/``--help``: help text
- ``-H HOST``/``--host HOST``: specify redis host
- ``-p PORT``/``--port PORT``: specify redis port
- ``-s SOCKET_PATH``/``--socket SOCKET_PATH``: connect to Unix socket at
  the specified path
- ``-w PASSWORD``/``--password PASSWORD``: password to use when connecting to redis
- ``-d DATABASE``/``--db DATABASE``: redis database to connect to (integer)
- ``-k PATTERN``/``--keys PATTERN`` (dumping only): dump only keys matching specified glob-style pattern
- ``-E ENCODING``/``-encoding ENCODING``: specify encoding to use
- ``-o PATH``/``--output PATH``: write dump to PATH rather than standard output
- ``-y``/``--pretty`` (dumping only): pretty-print JSON
- ``-A``/``--use-expireat`` (loading only): use ``expireat`` rather than ``ttl`` values in the dump
- ``-e``/``--empty`` (loading only): empty redis data set before loading
- ``-B BACKEND``/``--backend BACKEND`` (loading only): streaming backend to use

Streaming
---------

``dump`` will stream data unless ``pretty`` is given and ``True``.

``load`` will stream data if ijson_ or jsaone_ is installed. To determine whether
redis-dump-load supports streaming data load, examine
``redisdl.have_streaming_load`` variable. There are also
``redisdl.have_ijson`` and ``redisdl.have_jsaone`` variables indicating
presence of the respective library.

redis-dump-load prefers ijson over jsaone and does not specify a backend for
ijson by default, which as of this writing means that ijson's pure Python
backend will be used. To request a specific backend either pass it as
follows to the load methods::

    redisdl.load(io, streaming_backend='ijson-yajl2')

... or set the desired backend globally as follows::

    redisdl.streaming_backend = 'ijson-yajl2'

The backend argument takes form of "library-library backend", e.g.:
- ``ijson`` selects the default backend of ijson, which currently is the pure Python one.
- ``ijson-yajl2`` selects ijson with yajl2 backend.
- ``yajl2`` means the same things as ``ijson-yajl2`` for compatibility with older redis-dump-load versions.
- ``jsaone`` selects the jsaone backend.

Note: Streaming loading is substantially slower than lump loading.
To force lump loading of files, read the files in memory and invoke ``loads``
rather than ``load``.

jsaone support was added in redis-dump-load version 1.0.

TTL, EXPIRE and EXPIREAT
------------------------

When dumping, redis-dump-load dumps the TTL values for expiring keys
as well as calculated time when the keys will expire (``expireat``).
As Redis does not provide a command to retrieve absolute expiration time of
a key, the expiration time is calculated using the current time on the
*client*'s system. As such, if the time on the client system is not in sync
with time on the system where the Redis server is running, ``expireat``
values will be incorrect.

When loading, redis-dump-load by default uses the TTL values in the dump
(``ttl`` key) to set expiration times on the keys in preference to
``expireat`` values. This will maintain the expiration times of the keys
relative to the dump/load time but will change the absolute expiration time
of the keys. Using ``-A``/``--use-expireat`` command line option or
``use_expireat`` parameter to module functions will make redis-dump-load
use ``expireat`` values in preference to ``ttl`` values, setting expiring
keys to expire at the same absolute time as they had before they were dumped
(as long as system times are in sync on all machines involved).

Dumping and loading of TTL values and expiration times was added in
redis-dump-load version 1.0.

Unicode
-------

Redis operates on bytes and has no concept of Unicode or encodings.
JSON operates on (Unicode) strings and cannot serialize binary data. Therefore,
redis-dump-load has to encode Unicode strings into byte strings when
loading data into Redis and decode byte strings into Unicode strings
when dumping data from Redis.
By default redis-dump-load uses utf-8 for encoding data sent to Redis
and decoding data received from Redis.
This behavior matches redis-py, whose default encoding is utf-8.
A different encoding can be specified.

``dumps`` returns strings, that is, instances of ``str`` on Python 2
and instances of ``unicode`` on Python 3.

When dumping to an IO object using ``dump``, and the IO object accepts
byte strings (such as when a file is opened in binary mode),
redis-dump-load will ``.encode()`` the dumped data using the default
encoding in effect.

ijson's yajl2 backend can only decode ``bytes`` instances, not ``str``.
When loading data from a file opened in text mode and using ijson-yajl2,
redis-dump-load will encode the file data using utf-8 encoding before
passing the data to ijson. If this fails, try opening the file/stream in
binary mode.

jsaone can only decode text strings (``str`` instances), not ``bytes``.
When loading data from a file opened in binary mode and using jsaone,
redis-dump-load will decode the file data using the default encoding.
If this fails, you can change the default encoding or open the files in text
mode with the encoding appropriately specified in the ``open()`` call.

Concurrent Modifications
------------------------

redis-dump-load does not lock the entire data set it is dumping,
because Redis does not provide a way to do so.
As a result, modifications to the data set made while a dump is in progress
affect the contents of the dump.

Dependencies
------------

- redis-py_
- ijson_ or jsaone_ (optional, for streaming load)
- simplejson_ (Python 2.5 only)

Tests
-----

redis-dump-load has a test suite. To run it, install nose_ and run::

    nosetests

There are several tests that check for race conditions and as such take
a long time to run. To skip them, invoke nose thusly::

    nosetests -a '!slow'

License
-------

Released under the 2 clause BSD license.

.. _redis-dump: https://github.com/delano/redis-dump
.. _redis-py: https://github.com/andymccurdy/redis-py
.. _simplejson: http://pypi.python.org/pypi/simplejson/
.. _pickle: http://docs.python.org/library/pickle.html
.. _nose: https://nose.readthedocs.org/en/latest/
.. _ijson: https://pypi.python.org/pypi/ijson
.. _jsaone: http://pietrobattiston.it/jsaone
