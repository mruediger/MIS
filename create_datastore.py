#!/usr/bin/python

import sys
import os
import hashlib
import shutil
import pickle

import manifest
from datastore import Datastore

from lxml import etree

def usage():
    print sys.argv[0] + " manifest_name root_directory datastore"
    sys.exit(1)
    
def searchFiles(path,node,ds=None):
    if (not os.path.exists(path)):
        return

    node.stats = os.lstat(path)

    if (os.path.isdir(path) and 
        not os.path.islink(path)):
        for child in os.listdir(path):
            childpath = path + '/' + child
            if (os.path.isdir(childpath)):
                childnode = manifest.Directory(name = child)
            if (os.path.isfile(childpath)):
                childnode = manifest.File(name = child)
            node.addChild(childnode)
            searchFiles(path + '/' + child, childnode, ds)

    elif os.path.isfile(path):
        #calculate hash of file
        fobj = open(path,'r')
        hl = hashlib.sha1(fobj.read())
        fobj.close()
        node.hash = hl.hexdigest()
        #copy file to datastore
        if ds is not None:
            if (not os.path.exists(ds.getDirName(node.hash))):
                os.makedirs(ds.getDirName(node.hash))

            if (not os.path.exists(ds.getPath(node.hash))):
                shutil.copyfile(path,ds.getPath(node.hash))

if __name__ == '__main__':

        #PARSE ARGUMENTS
        if (len(sys.argv) < 3): usage()
        name = sys.argv[1]
        root = sys.argv[2]

        if (len(sys.argv) >= 3):
            datapath = sys.argv[3]
        else:
            datapath = None

        #SEARCH FOR FILES
        if (not os.path.isdir(root)):
            exit(1)
        tree = manifest.Directory('/')
        tree.stats = os.lstat(root)
        searchFiles(root, tree, Datastore(datapath))
         
        
        sys.setrecursionlimit(4000)
        pickle.dump(tree, open(sys.argv[4],'w'))
        #print etree.tostring(toXML(tree), pretty_print=True)

        test = input("blablubb")

