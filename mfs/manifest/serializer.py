# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.
"""manifest serializer

methods to create or read the manifest XML files
"""

__author__ = 'Mathias Ruediger <ruediger@blueboot.org>'

import os
import stat
import hashlib

from mfs.manifest.nodes import *

def fromPath(path, datastore=None):
    """
    traverses through path and creates a manifest object
    @
    """

    #check if directory contains unionfs
    if (os.path.exists(path + '/.unionfs')):
        unionfspath = path + '/.unionfs'
    else:
        unionfspath = None

    root = _searchFiles(path, '', datastore, '', unionfspath)
    return Manifest(root)

def fromXML(xml_file):
    """reads xml file and creates a manifest object"""
    parent = deque( [Directory("dummy")] )

    for action, element in etree.iterparse(xml_file, events=("start","end")):
        if (element.tag == "file" and action=="start"):
            #FIXME USE A FACTORY HERE!!!
            node = eval(element.get("type"))(element.get("name"))
            parent.append(node)

        if (element.tag.startswith("st_") and action=="end"):
            try:
                setattr(parent[len(parent) - 1], element.tag, eval(element.get("type"))(element.text))
            except TypeError, err:
                print element.tag + ":" + str(err)
                print "type is: " + str(type(element.text))

        if (element.tag == "hash" and action=="end"):
            parent[len(parent) - 1].hash = element.text

        if (element.tag == "orig_inode" and action=="end"):
            parent[len(parent) - 1].orig_inode = int(element.text)

        if (element.tag == "target" and action=="end"):
            parent[len(parent) - 1].target = element.text

        #because root will get removed to, we need a dummy
        if (element.tag == "file" and action=="end"):
            me = parent.pop() 
            mum = parent.pop()
            me.addTo(mum)
            parent.append(mum)
            element.clear()
    
    return Manifest(parent.pop()._children[0])


def _searchFiles(root, subpath, datastore, name, unionfspath):
    #the root + subpath split is needed for unionfs check
    path = root + subpath 
    stats = os.lstat(path)

    if stat.S_ISLNK(stats.st_mode):
        node = SymbolicLink(name, stats)
        node.target = os.readlink(path)
        return node

    if stat.S_ISREG(stats.st_mode):
        if name.startswith(".wh."):
            return DeleteNode(name[4:])

        # FIXME unionfs disabled
        #if (unionfspath and os.path.exists(unionfspath + subpath)
        #    and not os.path.isdir(unionfspath + subpath)):
        #    return DeleteNode(name)
        
        node = File(name, stats)
        #FIXME into constructor
        node.orig_inode = stats.st_ino
        hl = hashlib.sha256()
        fobj = open(path, 'r')
        while True:
            data = fobj.read(1024 * 1024)
            if not data: break
            hl.update(data)

        node.hash = hl.hexdigest()


        if (datastore is not None):
            datastore.saveData(node, path)
        return node
        
    if stat.S_ISDIR(stats.st_mode):
        node = Directory(name, stats)
        for childname in os.listdir(path):
            if (childname == '.unionfs'): continue

            childpath = subpath + '/' + childname
            child = _searchFiles(root, childpath, datastore, childname, unionfspath)
            child.addTo(node)

        return node

    if stat.S_ISBLK(stats.st_mode):
        return Device(name, stats)

    if stat.S_ISCHR(stats.st_mode):
        return Device(name, stats)

    if stat.S_ISFIFO(stats.st_mode):
        return FIFO(name, stats)
