Simhash Cluster
===============
Simhash takes an input vector of integers, and produces a single integer output
that's representative of that vector in the sense that _similar_ vectors yield
_similar_ hashes -- their resultant hashes are expected to differ by only a few
bits. With this in mind, simhash is often used in conjunction with a rolling
hash function on text to generate the input vector, and thus yield a hash that
corresponds to that block of text. In this way, you can quickly identify all the
documents that would be considered near-duplicates.

You can even construct tables to perform these queries very quickly indeed. 
Sadly, it can consume a fair amount of RAM, especially when you insert several 
hundred million or several billion hashes into the corpus of known hashes. And
so, a distributed form is necessary. This is that distributed form.

Architecture
============
There's one master node which slave nodes register with, at which point they are
assigned shards to serve and all queries to that shard will be served by that
node. The master and slaves communicate with zerorpc.

Adapters
========
Adapters are the mechanism by which the cluster is accessed; `simhash-cluster`
comes with two by default (one HTTP, and one zerorpc). All queries are directed
at the master node.

Storage
=======
There's an assumption that you'd like to persist your corpus of known hashes as
it might have developed over time. Like adapters, storage backends are pluggable
and simply must support a few methods like `save` and `load.`

Starting
========
The master node requires a yaml configuration file (an example file is included)
that describes the adapters and storage to use, as well as the simhash 
configuration. With the configuration in place:

    simhash-master --config example-config.yaml

This starts the master daemon (and adapters) running, and the master listening
on port 1234. Slaves should then be started (on any node) and pointing to the
master:

    simhash-slave <master hostname>:1234

Querying
========
Once the master node is running, you can begin querying. Assuming the master 
daemon is running on `localhost`:

    # Using the http interface
    import simplejson as json
    # Add a bunch of hashes
    requests.put('http://localhost:8080/hashes', json.dumps(range(10000)))
    # Find the first similar hash
    requests.get('http://localhost:8080/first/12345').content
    # Find all similar hashes
    requests.get('http://localhost:8080/all/12345').content
    # Remove a particular hash
    requests.delete('http://localhost:8080/hashes/12345')

And now using the `zerorpc` interface:

    import zerorpc
    c = zerorpc.Client('tcp://localhost:5678')
    # Insert hashes
    c.insert(*range(10000))
    # And find first and all
    c.find_first(*range(10000))
    c.find_all(*range(10000))
    # And remove all of them if you'd like
    c.remove(*range(10000))