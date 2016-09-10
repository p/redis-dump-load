#!/usr/bin/env python

import os.path
from distutils.core import setup

package_name = 'redis-dump-load'
package_version = '1.1'

doc_dir = os.path.join('share', 'doc', package_name)

data_files = ['LICENSE', 'README.rst']

setup(name=package_name,
    version=package_version,
    description='Dump and load redis databases',
    author='Oleg Pudeyev',
    author_email='oleg@bsdpower.com',
    url='http://github.com/p/redis-dump-load',
    py_modules=['redisdl'],
    install_requires=['redis'],
    data_files=[
        (doc_dir, data_files),
    ],
    entry_points={
        'console_scripts': [
            'redis-load = redisdl:main',
            'redis-dump = redisdl:main',
        ],
    },
    license="BSD",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: System :: Archiving',
    ],
)
