#! /usr/bin/env python

from . import logger
from .util import RangeMap

class Slave(object):
    def __init__(self, hostname):
        self.hostname = hostname
        self.rangemap = RangeMap()
    
    # Send configuration to this node
    def config(self, config):
        pass
    
    def load(self, start, end):
        '''Load and start serving an interval'''
        from simhash import Corpus
        logger.info('%s loading range [%i, %i)' % (self.hostname, start, end))
        self.rangemap.insert(start, end, Corpus(6, 3))
    
    def unload(self, start, end):
        '''Stop serving the provided interval'''
        logger.info('%s unloading range [%i, %i)' % (self.hostname, start, end))
        self.rangemap.remove(start, end)
    
    def save(self, start, end):
        '''Save the provided interval to permanent storage'''
        pass
    
    def find(self, h):
        '''Find the shard associated with the provided hash'''
        corpus = self.rangemap.find(h)
        if not corpus:
            return None
        return corpus
    
    def find_first(self, *hashes):
        '''Find the first near-duplicate of the provided hashes'''
        return [self.find(h).find_first(h) for h in hashes]
    
    def find_all(self, *hashes):
        '''Find all near-duplicates of the provided hashes'''
        return [self.find(h).find_all(h) for h in hashes]
    
    def insert(self, *insertions):
        '''Insert h in to the shard for q'''
        for q, h in insertions:
            self.find(q).insert(h)
    
    def remove(self, *removals):
        '''Remove h from the shard for q'''
        for q, h in removals:
            return self.find(q).remove(h)
    
    def register(self, host):
        import zerorpc
        c = zerorpc.Client('tcp://%s' % host)
        logger.info('Registering...')
        logger.info('Registered: %s' % repr(c.register(self.hostname)))
        c.close()
    