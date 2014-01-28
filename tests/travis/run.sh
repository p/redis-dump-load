#!/bin/sh

if test "$TEST" = quick; then
  make test-quick
elif test "$TEST" = slow; then
  make test-slow
else
  make test
fi
