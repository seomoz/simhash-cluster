#! /usr/bin/env python

import unittest

import os
import sys
base, name = os.path.split(os.path.abspath(__file__))
sys.path = [os.path.split(base)[0]] + sys.path

from smhcluster import master

class TestMaster(unittest.TestCase):
    def setUp(self):
        self.master = master.Master()
        for i in range(4):
            slave = master.Slave('slave-%i' % i, None)
            self.master.accept(slave)
    
    def test_insert_remove(self):
        # We should be able to appropriately insert and remove hashes
        h = int('101010101010', 2)
        q = int('101010101011', 2)
        self.master.insert(h)
        self.assertEqual(self.master.find_first(q), h)
        self.master.remove(h)
        self.assertEqual(self.master.find_first(q), 0)
    
    def test_find_first(self):
        # We should be able to find first
        h = int('101010101010', 2)
        q = int('101010101011', 2)
        self.master.insert(h)
        self.assertEqual(self.master.find_first(q), h)
    
    def test_find_all(self):
        # We should be able to find all
        hashes = [
            int('101010101010', 2),
            int('101010101011', 2),
            int('101010101111', 2)
        ]
        q = int('101010111010', 2)
        for h in hashes:
            self.master.insert(h)
        
        self.assertEqual(set(self.master.find_all(q)), set(hashes))
    
    def test_find_multiple(self):
        # We should be able to find queries even if the similar item wouldn't
        # normally map to the same shard as the original
        hashes = [
            int('101010101010', 2),
            int('101010101011', 2),
            int('101010101111', 2)
        ]
        q = int('101010101010', 2)
        
        for i in range(len(hashes)):
            hashes[i] = hashes[i] | (1 << 63)
            self.master.insert(hashes[i])
        
        self.assertEqual(set(self.master.find_all(q)), set(hashes))

if __name__ == '__main__':
    unittest.main()