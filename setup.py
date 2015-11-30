#!/usr/bin/env python

import os.path
from distutils.core import setup

package_name = 'redis-dump-load'
package_version = '0.4.0'

doc_dir = os.path.join('share', 'doc', package_name)

data_files = ['LICENSE', 'README.rst']

setup(name=package_name,
    version=package_version,
    description='Dump and load redis databases',
    author='Oleg Pudeyev',
    author_email='oleg@bsdpower.com',
    url='http://github.com/p/redis-dump-load',
    py_modules=['redisdl'],
    data_files=[
        (doc_dir, data_files),
    ],
)
