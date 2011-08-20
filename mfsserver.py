#!/usr/bin/python

import sys

from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

from mfs.repository import FileRepository
from mfs.server import MFSServer

def run(repo, port, autopatch):
    repository = FileRepository(repo)

    server = Server(('', int(port)))
    server.register_instance(MFSServer(repository, None))
    server.serve_forever()

if __name__ == '__main__':
    try:
        repo = sys.argv[1]
        port = sys.argv[2]
        if len(sys.argv) > 3:
            filterscript = sys.argv[3]
            run(repo, port, autopatch)
        else:
            run(repo, port, None)
    except IndexError:
        print "usage {0} repository port".format(sys.argv[0])
