# Provides a zerorpc interface to the cluster

import zerorpc

from . import Server as _Server

class Server(_Server):
    # Accepts a cluster, which contains all the python objects needed to make 
    # queries
    def __init__(self, cluster):
        self.cluster = cluster
    
    # Idempotently accept new configurations, raising exceptions when 
    # malconfigured
    def config(self, config):
        for key in config.keys():
            if key not in ('port'):
                raise KeyError('Unknown configuration option %s' % key)
        
        self.port = config.get('port', 1234)
        if hasattr(self, 'server'):
            self.server.stop()
        
        self.server = zerorpc.Server(self.cluster)
        self.server.bind('tcp://0.0.0.0:%i' % self.port)
    
    # Serve forever
    def listen(self):
        self.server.run()
    
    # Stop
    def stop(self):
        self.server.stop()
        del self.server
