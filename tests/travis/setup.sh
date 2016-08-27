#!/bin/sh

set -e

pip install -r requirements-dev.txt

case "$STREAMING_BACKEND" in
  ijson)
    pip install ijson;;
  ijson-yajl)
    pip install ijson
    git clone https://github.com/lloyd/yajl
    cd yajl
    git checkout 1.0.12
    ./configure --prefix=/home/travis/local
    make
    make install
    ;;
  ijson-yajl2)
    pip install ijson
    git clone https://github.com/lloyd/yajl
    cd yajl
    git checkout 2.0.0
    ./configure --prefix=/home/travis/local
    make
    make install
    ;;
  jsaone)
    # broken
    #pip install jsaone
    
    pip install cython
    curl -o jsaone.tar.gz 'http://www.pietrobattiston.it/gitweb?p=jsaone.git;a=snapshot;h=master;sf=tgz'
    tar xf jsaone.tar.gz
    cd jsaone-master-*
    python setup.py install
    ;;
  "")
    ;;
  *)
    echo "Unknown streaming backend $STREAMING_BACKEND" 1>&2
    exit 10;;
esac
