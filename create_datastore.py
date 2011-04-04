#!/usr/bin/python

import sys
import os
import hashlib
import shutil

import manifest
from datastore import Datastore

from lxml import etree

def usage():
    print sys.argv[0] + " manifest_name root_directory"
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
                node.addChild(manifest.Directory(name = child))
                searchFiles(path + '/' + child , node.children[child], ds)
            if (os.path.isfile(childpath)):
                node.addChild(manifest.File(name = child))
                searchFiles(path + '/' + child, node.children[child], ds)

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

def toXML(node):
    xml = etree.Element("file")
    if (node.is_directory()):
        xml.attrib['type'] = "dir"
    else:
        xml.attrib['type'] = "file"
    
    for k in node.__slots__:
        if (not (k == 'children' or k == 'stats')): 
            xmlchild = etree.SubElement(xml, k)
            xmlchild.attrib['type'] = type(getattr(node,k)).__name__
            xmlchild.text = str(getattr(node,k))

    for k in dir(node.stats):
        if (k.startswith('st_')):
            xmlchild = etree.SubElement(xml,k)
            xmlchild.attrib['type'] = type(getattr(node.stats,k)).__name__
            xmlchild.text = str(getattr(node.stats,k))

    if (node.is_directory()):
        for child in node.children.values():
            xml.append(toXML(child))
    return xml

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
             
        print etree.tostring(toXML(tree), pretty_print=True)
