# Provides a JSON interface to access the simhash cluster

# We need bottle for the server, and requests for the client
import gevent.monkey
gevent.monkey; gevent.monkey.patch_all()
import bottle
import requests
from bottle import run, request, abort, Bottle

try:
    import simplejson as json
except ImportError:
    import json

from . import Server as _Server
from . import Client as _Client

class Server(_Server):
    # Accepts a cluster, which contains all the python objects needed to make 
    # queries
    def __init__(self, cluster):
        self.cluster = cluster
        self.root    = Bottle()

    # Idempotently accept new configurations, raising exceptions when 
    # malconfigured
    def config(self, config):
        for key in config.keys():
            if key not in ('port'):
                raise KeyError('Unknown configuration option %s' % key)
        
        self.port = config.get('port', 8080)
    
    def first(self, query=None):
        if query:
            return json.dumps(self.cluster.find_first(int(query)))
        return json.dumps(
            self.cluster.find_first(*json.load(request.body)))
    
    def all(self, query=None):
        if query:
            return json.dumps(self.cluster.find_all(int(query)))
        return json.dumps(
            self.cluster.find_all(*json.load(request.body)))

    def insert(self, h=None):
        if h:
            return json.dumps(self.cluster.insert(int(h)))
        return json.dumps(
            self.cluster.insert(*json.load(request.body)))
    
    def remove(self, h=None):
        if h:
            return json.dumps(self.cluster.remove(int(h)))
        return json.dumps(
            self.cluster.remove(*json.load(request.body)))
    
    # Serve forever
    def listen(self):
        # We're doing this a little oddly, because the server is an instance, so
        # we have to wait until we have an object so that we can attach the
        # route to a method bound to this instance.
        self.root.get(   '/first/<query>'  )(self.first)   # Single
        self.root.post(  '/first'          )(self.first)   # Bulk
        self.root.get(   '/all/<query>'    )(self.all)     # Single
        self.root.post(  '/all'            )(self.all)     # Bulk
        self.root.put(   '/hashes/<h>'     )(self.insert)  # Single
        self.root.put(   '/hashes'         )(self.insert)  # Bulk
        self.root.delete('/hashes/<h>'     )(self.remove)  # Single
        self.root.delete('/hashes/'        )(self.remove)  # Bulk
        
        # And run it!
        run(self.root, host='localhost', port=8080, server='gevent')
        print 'HTTP listening...'
    
    # Stop
    def stop(self):
        pass

class Client(_Client):
    # Accepts a host to which to speak
    def __init__(self, host):
        self.host = host

    # Check for /any/ near-duplicate documents
    def find_first(self, query):
        return json.loads(requests.get(self.host + '/first/' + query).content)

    # Check for /all/ near-duplicates
    def find_all(self, query):
        return json.loads(requests.get(self.host + '/all/' + query).content)

    # Bulk form of find_first
    def find_first_bulk(self, queries):
        r = requests.post(self.host + '/first', data=json.dumps(queries))
        return json.loads(r.content)
    
    # Bulk form of find_all
    def find_all_bulk(self, queries):
        r = requests.post(self.host + '/all', data=json.dumps(queries))
        return json.loads(r.content)
    
    # Insert a hash
    def insert(self, h):
        return json.loads(requests.put(self.host + '/hashes/' + h))
    
    # Bulk form of insert
    def insert_bulk(self, hashes):
        r = requests.put(self.host + '/hashes', data=json.dumps(hashes))
        return json.loads(r.content)
    
    # Remove a hash
    def remove(self, h):
        return json.loads(requests.delete(self.host + '/hashes/' + h))
    
    # Bulk form of remove
    def remove_bulk(self, hashes):
        r = requests.delete(self.host + '/hashes', data=json.dumps(hashes))
        return json.loads(r.content)
