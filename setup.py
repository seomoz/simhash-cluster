#! /usr/bin/env python

from distutils.core import setup

setup(name           = 'smhcluster',
    version          = '0.1.0',
    description      = 'Cluster for Near-Duplicate Detection with Simhash',
    url              = 'http://github.com/seomoz/simhash-cluster',
    author           = 'Dan Lecocq',
    author_email     = 'dan@seomoz.org',
    packages         = ['smhcluster', 'smhcluster.adapters'],
    package_dir      = {
        'smhcluster': 'smhcluster',
        'smhcluster.adapters': 'smhcluster/adapters'
    },
    scripts          = [
        'bin/simhash-master',
        'bin/simhash-slave'
    ],
    dependencies     = [
        'simhash',   # For obvious reasons
        'boto',      # For persistence to S3
        'bottle',    # For the HTTP adapter
        'gevent',    # For non-blocking goodness
        'requests',  # For making real http requests
        'zerorpc'    # For RPC with gevent, zeromq
    ],
    classifiers      = [
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'
    ],
)
