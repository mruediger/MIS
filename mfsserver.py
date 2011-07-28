#!/usr/bin/python

from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

from mfs.repository import FileRepository
from mfs.server import MFSServer

def run():
    repository = FileRepository('tmp/repository')

    server = Server(('', 4321))
    server.register_instance(MFSServer(repository))
    server.serve_forever()

if __name__ == '__main__':
    run()
