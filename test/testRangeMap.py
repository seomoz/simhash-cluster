#! /usr/bin/env python

import unittest

import os
import sys
base, name = os.path.split(os.path.abspath(__file__))
sys.path = [os.path.split(base)[0]] + sys.path

from smhcluster.util import RangeMap

class TestRangeMap(unittest.TestCase):
    def setUp(self):
        self.rm = RangeMap()
    
    def test_insert_remove(self):
        # We should be able to insert new ranges and find them, and remove
        self.assertEqual(self.rm.find(100), None)
        self.rm.insert(0, 200, 'testing')
        self.assertEqual(self.rm.find(100), 'testing')
        self.rm.remove(0, 200)
        self.assertEqual(self.rm.find(100), None)
    
    def test_too_low(self):
        # If an index is too low for our ranges, then we should find None
        self.rm.insert(100, 200, 'testing')
        self.assertEqual(self.rm.find(99), None)
    
    def test_too_high(self):
        # If it's not inside one of our ranges, we should find None
        self.rm.insert(0, 100, 'testing')
        self.assertEqual(self.rm.find(101), None)
    
    def test_boundary(self):
        # When items are on the boundary, we should still find something
        self.rm.insert(100, 200, 'testing')
        self.assertEqual(self.rm.find(200), 'testing')
        self.assertEqual(self.rm.find(100), 'testing')
    
    def test_multiple(self):
        # When we have multiple ranges, we should be able to find the right one
        self.rm.insert(100, 200, 'cheese')
        self.rm.insert(300, 400, 'shop')
        self.rm.insert(500, 600, 'sketch')
        self.assertEqual(self.rm.find(150), 'cheese')
        self.assertEqual(self.rm.find(350), 'shop')
        self.assertEqual(self.rm.find(550), 'sketch')
    
    def test_remove_nonexistent(self):
        # When we ask to find rid of a range where we have the start range, but
        # the ends don't match, we should find an exception
        self.rm.insert(100, 200, 'testing')
        self.assertRaises(Exception, self.rm.remove, 100, 300)

if __name__ == '__main__':
    unittest.main()