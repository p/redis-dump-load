#!/usr/bin/env python

from distutils.core import setup

setup(name='redis-dump-load',
    version='0.3.0',
    description='Dump and load redis databases',
    author='Oleg Pudeyev',
    author_email='oleg@bsdpower.com',
    url='http://github.com/p/redis-dump-load',
    py_modules=['redisdl'],
    data_files=['LICENSE', 'README.rst'],
)
