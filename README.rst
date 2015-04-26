redis-dump-load
===============

.. image:: https://api.travis-ci.org/p/redis-dump-load.png
  :target: https://travis-ci.org/p/redis-dump-load

Dumps Redis data sets into a format suitable for long-term storage
(currently JSON) and loads data from such dump files back into Redis.

redis-dump_ was there first, but
it is written in Ruby.

The output format is intended to be compatible with redis-dump.

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
        # currently does not stream data
        redisdl.load(f)

Note that while ``dump`` will stream data, ``load`` currently will not
(``load`` will read the entire file contents into a string, parse it,
then walk the resulting data structure and load it into redis).

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
- ``empty`` (boolean, load only): empty the redis data set before loading the
  data

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
- ``-w PASSWORD``/``--password PASSWORd``: password to use when connecting to redis
- ``-d DATABASE``/``--db DATABASE``: redis database to connect to (integer)
- ``-E ENCODING``/``-encoding ENCODING``: specify encoding to use
- ``-o PATH``/``--output PATH``: write dump to PATH rather than standard output
- ``-y``/``--pretty`` (dumping only): pretty-print JSON
- ``-e``/``--empty`` (loading only): empty redis data set before loading

Dependencies
------------

- redis-py_
- simplejson_ (Python 2.5 only)

Unicode
-------

Redis operates on bytes and has no concept of Unicode or encodings.
JSON operates on Unicode strings and cannot serialize binary data. Therefore,
redis-dump-load has to encode Unicode strings into byte strings when
loading data into Redis and decode byte strings into Unicode strings
when dumping data from Redis.
By default redis-dump-load uses utf-8 for encoding and decoding.
This behavior matches redis-py, whose default encoding is utf-8.
A different encoding can be specified.

Concurrent Modifications
------------------------

redis-dump-load does not lock the entire data set it is dumping,
because Redis does not provide a way to do so.
As a result, modifications to the data set made while a dump is in progress
affect the contents of the dump.

License
-------

Released under the 2 clause BSD license.

.. _redis-dump: https://github.com/delano/redis-dump
.. _redis-py: https://github.com/andymccurdy/redis-py
.. _simplejson: http://pypi.python.org/pypi/simplejson/
.. _pickle: http://docs.python.org/library/pickle.html
