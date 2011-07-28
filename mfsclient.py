#!/usr/bin/python

"""
basic remote client
"""

import xmlrpclib
import pickle
import sys

from lxml import etree

import mfs

def print_manifest(host, name, version=""):
    '''prints the according manifest to stdout'''
    client = xmlrpclib.ServerProxy(host)
    manifest = pickle.loads(client.getManifest(name, version))
    print etree.tostring(manifest.toXML(), pretty_print=True)
    

def listVersions(host, name):
    '''list all versions of image "name"'''
    client = xmlrpclib.ServerProxy(host)
    print client.listVersions(name)

def pull(host, config, name, version, folder):
    '''pulls image "name" with version "version" into folder "folder"'''
    client = xmlrpclib.ServerProxy(host)
    datastore = mfs.datastore.Datastore(config.datastore)
    manifest  = pickle.loads(client.getManifest(name, version))
    manifest.export(folder, datastore)

def update(name, oldversion, version, folder):
    '''updates image "name" with version "oldversion" in folder "folder" to "version"'''
    pass


if __name__ == "__main__":
    
    help_message = """usage: """

    try:
        with open(sys.argv[1]) as configfile:
            config = mfs.config.Config(configfile)
        host   = sys.argv[2]
        action = sys.argv[3]
        arguments = sys.argv[4:]
    except IndexError:
        print help_message
        print sys.argv[0] + " too few arguments"
        sys.exit(1)

    if (action == "print"):
        if len(arguments) == 1:
            print_manifest(host, arguments[0])
        elif len(arguments) == 2:
            print_manifest(host, arguments[0],arguments[1])
        else:
            print "usage {0} print NAME [VERSION]".format(sys.argv[0])
            sys.exit(1)
    
    if (action == "versions"):
        try:
            listVersions(host, arguments[0])
        except IndexError:
            print "usage {0} list NAME".format(sys.argv[0])
            sys.exit(1)

    if (action == "pull"):
        try:
            pull(host, config, arguments[0], arguments[1], arguments[2])
        except IndexError:
            print "usage {0} pull NAME VERSION DESTINATION".format(sys.argv[0])
