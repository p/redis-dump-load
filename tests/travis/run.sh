#!/bin/sh

set -e

NOSETESTS="nosetests -v"

export LD_LIBRARY_PATH=/home/travis/local/lib

echo Streaming backend: `python -c 'import redisdl; print(redisdl.default_streaming_backend)'`

if test "$TEST" = slow; then
  $NOSETESTS -a '!yajl2,slow'
else
  $NOSETESTS -a '!yajl2,!slow'
fi

if test -n "$YAJL2"; then
  $NOSETESTS -a 'yajl2,!slow'
fi
