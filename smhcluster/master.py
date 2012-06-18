#! /usr/bin/env python

from .util import RangeMap

class Slave(object):
    def __init__(self, hostname, conn):
        self.hostname   = hostname
        self.connection = conn
        
        self.rangemap   = RangeMap()
    
    # Send configuration to this node
    def config(self, config):
        pass
    
    def load(self, start, end):
        from simhash import Corpus
        logger.debug(
            '%s accepting range [%i, %i)' % (self.hostname, start, end))
        self.rangemap.insert(start, end, Corpus(6, 3))
    
    def unload(self, start, end):
        self.rangemap.remove(start, end)
    
    def save(self, start, end):
        pass
    
    def find(self, h):
        corpus = self.rangemap.find(h)
        if not corpus:
            return None
        return corpus
    
    def find_first(self, h):
        logger.debug('%s find first %i' % (self.hostname, h))
        return self.find(h).find_first(h)
    
    def find_all(self, h):
        logger.debug('%s find all %i' % (self.hostname, h))
        return self.find(h).find_all(h)
    
    def insert(self, q, h):
        logger.debug('%s insert %i' % (self.hostname, h))
        return self.find(q).insert(h)
    
    def remove(self, q, h):
        logger.debug('%s remove %i' % (self.hostname, h))
        return self.find(q).remove(h)

# This is the master node object. It talks to slave nodes to determine both
# their availability and health and to answer queries.
class Master(object):
    # The number of shards 
    shards          = 1024
    max_node_shards = 256
    differing_bits  = 3
    blocks          = 6
    
    class RangeUnassigned(Exception):
        def __init__(self, value):
            Exception.__init__(self, value)
    
    def __init__(self):
        self.rangemap = RangeMap()
        for start, end in self.ranges():
            self.rangemap.insert(start, end, None)
        
        # A mapping of hostnames to slave objects
        self.slaves = {}
    
    def ranges(self):
        # Return a list of tuples (start, end) that we need
        results = []
        for i in range(self.shards):
            start =  i      * (1 << 64) / self.shards
            end   = (i + 1) * (1 << 64) / self.shards
            results.append((start, end))
        return results
    
    def unassigned(self):
        # Get a list of tuples (start, end) of ranges that are unassigned
        return [(s, e) for s, e, i in self.rangemap if i == None]
        
    def accept(self, slave):
        # Accept a new slave. First, determine how many shards we're going to
        # give to each node once we add this new one
        count = min(self.max_node_shards, self.shards / (len(self.slaves) + 1))
        assign = self.unassigned()[0:count]
        if (len(assign) < count):
            # This is where we'd figure which nodes to steal shards from
            pass
        
        logger.info('Assigning %i to %s' % (count, slave.hostname))
        self.slaves[slave.hostname] = slave
        for start, end in assign:
            slave.load(start, end)
            self.rangemap.insert(start, end, slave)
    
    def config(self, config):
        pass
    
    def listen(self):
        # Listen for nodes trying to connect
        pass
    
    def find(self, h):
        slave = self.rangemap.find(h)
        if not slave:
            raise Master.RangeUnassigned('%i unavailable' % h)
        return slave
    
    def find_first(self, h):
        return self.find(h).find_first(h)
    
    def find_all(self, h):
        return self.find(h).find_all(h)
    
    def insert(self, h):
        # Because we map each query onto a range, we have to make sure that each
        # conceivable match for any query in that range is available. So for a 
        # query for 0110100101101101, we'd map it onto a range, and return the
        # results from that range. However, it's more than likely that a number
        # 1110100101101101 would not be mapped to the same range. So, it doesn't
        # suffice to simply /insert/ based on ranges alone. We actually have to
        # insert it into a number of ranges.
        #
        # In particular, if we are configured to use 3 differing bits, then we 
        # need to insert it into each of the ranges indicated by flipping the 
        # 3 MSBs of the hash to insert by 0, 1, 2, 3, 4, 5, 6 and 7.
        for i in range(1 << self.differing_bits):
            q = h ^ (i << (64 - self.differing_bits))
            logger.debug('Looking up %s (%i)' % (bin(q), q))
            self.find(q).insert(q, h)
        return True
    
    def remove(self, h):
        # See the note in `insert`
        for i in range(1 << self.differing_bits):
            q = h ^ (i << (64 - self.differing_bits))
            logger.debug('Looking up %s (%i)' % (bin(q), q))
            self.find(q).remove(q, h)
        return True