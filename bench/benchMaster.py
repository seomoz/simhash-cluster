#! /usr/bin/env python

import os
import sys
base, name = os.path.split(os.path.abspath(__file__))
sys.path = [os.path.split(base)[0]] + sys.path

from smhcluster import master

m = master.Master()
for i in range(4):
    slave = master.Slave('slave-%i' % i, None)
    m.accept(slave)

class timer(object):
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        self.start = -time.time()
        print 'Starting %s...' % self.name
    
    def __exit__(self, t, v, tb):
        self.start += time.time()
        print '         %s: %fs' % (self.name, self.start)

import time
import random

with timer('hashes and queries'):
    hashes  = [random.randint(0, 1 << 63) for i in range(100000)]
    queries = [random.randint(0, 1 << 63) for i in range(100000)]

with timer('insert %i' % len(hashes)):
    for h in hashes:
        m.insert(h)

with timer('find_first %i' % len(queries)):
    for q in queries:
        m.find_first(q)

with timer('find_all %i' % len(queries)):
    for q in queries:
        m.find_all(q)

with timer('removes %i' % len(hashes)):
    for h in hashes:
        m.remove(h)
