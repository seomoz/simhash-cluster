# All adapters must implement the Server interface. This determines how clients
# will access the master server (via HTTP, etc.). Adapters should also provide
# at least a reference client implementation as well, also provided.

class Server(object):
    # Accepts a cluster, which contains all the python objects needed to make 
    # queries
    def __init__(self, cluster):
        self.cluster = cluster
    
    # Idempotently accept new configurations, raising exceptions when 
    # malconfigured
    def config(self, config):
        pass
    
    # Serve until we say stop
    def listen(self):
        pass
    
    # Stop serving
    def stop(self):
        pass

class Client(object):
    # Accepts a host to which to speak
    def __init__(self, host):
        self.host = host
    
    # Check for /any/ near-duplicate documents
    def find_first(self, query):
        pass
    
    # Check for /all/ near-duplicates
    def find_all(self, query):
        pass
    
    # Bulk form of find_first
    def find_first_bulk(self, queries):
        pass
    
    # Bulk form of find_all
    def find_all_bulk(self, queries):
        pass
    
    # Insert a hash
    def insert(self, h):
        pass
    
    # Bulk form of insert
    def insert_bulk(self, hashes):
        pass
    
    # Remove a hash
    def remove(self, h):
        pass
    
    # Bulk form of remove
    def remove_bulk(self, hashes):
        pass