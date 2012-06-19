#! /usr/bin/env python

from . import logger
from .util import RangeMap

from collections import defaultdict

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
        # Our current configuration
        self._config = {}
    
    def ranges(self):
        # Return a list of tuples (start, end) that we need
        results = []
        for i in range(self.shards):
            start =  i      * (1 << 64) / self.shards
            end   = (i + 1) * (1 << 64) / self.shards
            results.append((start, end-1))
        return results
    
    def unassigned(self):
        # Get a list of tuples (start, end) of ranges that are unassigned
        return [(s, e) for s, e, i in self.rangemap if i == None]
        
    def register(self, hostname):
        # Accept a new slave. First, determine how many shards we're going to
        # give to each node once we add this new one
        count = min(self.max_node_shards, self.shards / (len(self.slaves) + 1))
        assign = self.unassigned()[0:count]
        if (len(assign) < count):
            # We need to actually steal shards from some of the existing slaves
            # so we should figure out where to take them from
            slaves = defaultdict(list)
            for s, e, i in self.rangemap:
                if i != None:
                    slaves[i].append((s, e))
            
            # Now make a list of tuples based on this
            slaves = [(len(v), s, v) for s, v in slaves.items()]
            slaves.sort()
            slaves.reverse()
            for l, slave, shards in slaves:
                # Take up to l-count from this guy
                ct = min(l - count, count - len(assign))
                nw = shards[0:ct]
                assign.extend(nw)
                for start, end in nw:
                    slave.unload(start, end)
                    logger.info('Reassigning [%i, %i) from %s to %s' % (start, end, repr(slave), hostname))
        
        import zerorpc
        logger.info('Assigning %i to %s' % (count, hostname))
        slave = zerorpc.Client('tcp://%s' % hostname)
        self.slaves[hostname] = slave
        for start, end in assign:
            slave.load(start, end)
            self.rangemap.insert(start, end, slave)
        
        # Send it its updated configuration
        slave.config(self._config)
    
    def deregister(self, hostname):
        # When deregistering a node, we should redistribute all the keys
        # associated with this particular host
        if isinstance(hostname, basestring):
            slave = self.slaves.pop(hostname)
        else:
            slave = hostname
            for k, v in self.slaves.items():
                if slave == v:
                    o = self.slaves.pop(k)
        
        assign = [(s, e) for s, e, i in self.rangemap if i == slave]
        count  = min(self.max_node_shards, self.shards / (len(self.slaves)) + 1)
        # Alright, assign these ranges to the remaining slaves. Keep filling up
        # slaves until they're full
        for slave in self.slaves.values():
            ct = len([(s, e) for s, e, i in self.rangemap if i == slave])
            for i in range(count - ct):
                if not assign:
                    break
                s, e = assign.pop(0)
                slave.load(s, e)
                self.rangemap.insert(s, e, slave)
                logger.info('Reassigning [%i, %i) to %s' % (s, e, repr(slave)))
        
        # Unassign all the remaining shards
        for s, e in assign:
            self.rangemap.insert(s, e, None)
    
    def stats(self):
        # Return the distribution of the shards
        slaves = defaultdict(list)
        for s, e, i in self.rangemap:
            if i != None:
                slaves[i].append((s, e))
        
        return dict(((repr(s), len(shards)) for s, shards in slaves.items()))
    
    def config(self, config):
        self._config = config
        # Propagate the configuration to all the slaves
        for slave in self.slaves.values():
            slave.config(config)
    
    def listen(self):
        # Listen for nodes trying to connect
        import zerorpc
        self.server = zerorpc.Server(self)
        self.server.bind('tcp://0.0.0.0:1234')
        self.server.run()
    
    def find(self, h):
        slave = self.rangemap.find(h)
        if not slave:
            raise Master.RangeUnassigned('%i unavailable' % h)
        return slave
    
    def find_first(self, *hashes):
        destinations = defaultdict(list)
        for h in hashes:
            destinations[self.find(h)].append(h)
        
        results = []
        for k, queries in destinations.items():
            results.extend(zip(queries, k.find_first(*queries)))
            logger.info('Finished querying %s' % k)
        return results
    
    def find_all(self, *hashes):
        destinations = defaultdict(list)
        for h in hashes:
            destinations[self.find(h)].append(h)
        
        results = []
        for k, queries in destinations.items():
            results.extend(zip(queries, k.find_all(*queries)))
            logger.info('Finished querying %s' % k)
        return results
    
    def insert(self, *hashes):
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
        #
        # This is a map of destinations to the queries
        destinations = defaultdict(list)        
        for h in hashes:
            for i in range(1 << self.differing_bits):
                q = h ^ (i << (64 - self.differing_bits))
                logger.debug('Looking up %s (%i)' % (bin(q), q))
                destinations[self.find(q)].append((q, h))
        
        for k, insertions in destinations.items():
            k.insert(*insertions)
            logger.info('Finished inserting %s' % k)
        return True
    
    def remove(self, *hashes):
        # See the note in `insert`
        destinations = defaultdict(list)        
        for h in hashes:
            for i in range(1 << self.differing_bits):
                q = h ^ (i << (64 - self.differing_bits))
                logger.debug('Looking up %s (%i)' % (bin(q), q))
                destinations[self.find(q)].append((q, h))
        
        for k, removals in destinations.items():
            k.remove(*removals)
            logger.info('Finished inserting %s' % k)
        return True