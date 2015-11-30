#!/bin/sh

set -e

NOSETESTS=nosetests

if test "$TEST" = slow; then
  $(NOSETESTS) -a '!yajl2,slow'
else
  $(NOSETESTS) -a '!yajl2,!slow'
fi

if test -n "$YAJL2"; then
  $(NOSETESTS) -a 'yajl2,!slow'
fi
