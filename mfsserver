#!/usr/bin/python

import sys

from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

from mfs.repository import FileRepository
from mfs.server import MFSServer
from mfs.datastore import Datastore
from mfs.autopatcher import Autopatcher

def run(repo, port, autopatcher, datastore):
    repository = FileRepository(repo)

    server = Server(('', int(port)))
    server.register_instance(MFSServer(repository, autopatcher, datastore))
    server.serve_forever()

if __name__ == '__main__':
    try:
        repo = sys.argv[1]
        port = sys.argv[2]
        if len(sys.argv) > 3:
            autopatcher = Autopatcher(sys.argv[3])
            datastore = Datastore(sys.argv[4])
            run(repo, port, autopatcher, datastore)
        else:
            run(repo, port, None, None)
    except IndexError:
        print "usage {0} repository port [ patchfile_path datastore_path ]".format(sys.argv[0])
