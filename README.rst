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

redis-dump-load may be used as a module and also as a command-line tool.

To use it as a module, import it in your program and use the pickle-like
interface: load, loads, dump, dumps. load and dump will stream the data.

To use it as a command-line tool, execute the script. If the basename of
the script contains the word "load", the operating mode will be set to
load data; otherwise the mode will be to dump data. -l may be used to
change the mode to load regardless of what the script is called.

Example hardlink shortcuts:

::

	ln redisdl.py redis-dump
	ln redisdl.py redis-load

Symlinks work equally well.

Dependencies

 - redis-py_
 - simplejson_ (Python 2.5 only)

License
-------

Released under the 2 clause BSD license.

.. _redis-dump: https://github.com/delano/redis-dump
.. _redis-py: https://github.com/andymccurdy/redis-py
.. _simplejson: http://pypi.python.org/pypi/simplejson/
