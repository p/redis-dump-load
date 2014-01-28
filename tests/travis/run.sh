#!/bin/sh

if test "$TEST" = slow; then
  make test-slow
else
  make test-quick
fi
