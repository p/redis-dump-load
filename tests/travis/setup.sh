#!/bin/sh

set -e

pip install -r requirements-dev.txt

case "$STREAMING_BACKEND" in
  ijson)
    pip install ijson;;
  ijson-yajl)
    pip install ijson yajl;;
  ijson-yaql2)
    pip install ijson yajl2;;
  jsaone)
    pip install jsaone;;
  "")
  *)
    echo "Unknown streaming backend $STREAMING_BACKEND" 1>&2
    exit 10;;
esac
