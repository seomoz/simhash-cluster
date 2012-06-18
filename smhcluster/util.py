#! /usr/bin/env python

# A few utility functions
def klass(s):
    '''Given a string, return the class associated with it'''
    mod = __import__(s.rpartition('.')[0])
    for m in s.split('.')[1:-1]:
        mod = getattr(mod, m)
    return getattr(mod, s.rpartition('.')[2])

import bisect

# A map of a set of ranges to items. It assumes that no two ranges overlap, but
# it does not enforce that constraint. This class isn't optimized for fast 
# insertions or deletions -- for the time being, it's standing in for an 
# interface, which may be improved upon in the future
class RangeMap(object):
    class RangeMatchException(Exception):
        def __init__(self, val):
            Exception.__init__(self, val)
    
    def __init__(self):
        # These are the starts of each of the ranges this holds
        self.starts = []
        # A map from the start range to a tuple (end, item), which corresponds 
        # to the start of the range
        self.items  = {}
    
    def __len__(self):
        return len(self.starts)
    
    def __iter__(self):
        results = []
        for start in self.starts:
            end, item = self.items[start]
            results.append((start, end, item))
        return iter(results)
    
    # Find the item responsible for this range, remove and return it
    def remove(self, start, end):
        if start in self.items:
            oend, item   = self.items.pop(start)
            if oend == end:
                self.starts = [i for i in self.starts if i != start]
                return item
            self.items[start] = (oend, item)
            raise RangeMap.RangeMatchException('%i != %i' % (oend, end))
        return None
    
    # Insert a new item that is responsible for the provided range
    def insert(self, start, end, item):
        if start not in self.items:
            self.starts.append(start)
            self.starts.sort()
        self.items[start] = (end, item)
    
    # Get the item responsible for the provided range. If no suitable item can 
    # be found, then it returns None
    def find(self, index):
        # If we don't have any items, then we're SOL
        i = bisect.bisect(self.starts, index)
        if (i == 0) or (i > len(self.starts)):
            return None
        
        start = self.starts[i-1]
        # If the start we found is still greater than index, we don't have one
        if start > index:
            return None
        
        end, item = self.items[start]
        # If it's outside of its range, then we've got a problem
        if end < index:
            return None
        
        return item
    
    # Index is based off of the start range
    def __getitem__(self, index):
        return self.items[index]
