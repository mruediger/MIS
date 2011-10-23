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

class NullNode(object):

    def addTo(self, directory):
	pass

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
    node = None

    for action, element in etree.iterparse(xml_file, events=("start","end")):
        if (action == "start"):
            if (element.tag == "file"):
                #FIXME USE A FACTORY HERE!!!
                parent = node
                node = eval(element.get("type"))(element.get("name"))

                if parent:
                    node.addTo(parent)
                continue
        else:
            if (element.tag[:3] == "st_"):
                try:
                    setattr(node.stats, element.tag, eval(element.get("type"))(element.text))
                except:
                    print node.name
                    print element.tag
                    print "type is: " + str(element.get("type"))
                continue

            if (element.tag == "hash"):
                node.hash = element.text
                continue

            if (element.tag == "orig_inode"):
                node.orig_inode = int(element.text)
                continue

            if (element.tag == "target"):
                node.target = element.text
                continue

            if (element.tag == "rdev"):
                node.rdev = int(element.text)
                continue

            if (element.tag == "file"):
                if node.parent:
                    node = node.parent            
    
    return Manifest(node)

def _searchFiles(root, subpath, datastore, name, unionfspath):
    #the root + subpath split is needed for unionfs check
    path = root + subpath 
    orig_stats = os.lstat(path)
    stats = Stats(orig_stats)

    if stat.S_ISLNK(stats.st_mode):
        node = SymbolicLink(name, stats)
        node.target = os.readlink(path)
        return node

    if stat.S_ISREG(stats.st_mode):
        if name.startswith(".wh."):
            return WhiteoutNode(name[4:], stats)

        # FIXME unionfs disabled
        #if (unionfspath and os.path.exists(unionfspath + subpath)
        #    and not os.path.isdir(unionfspath + subpath)):
        #    return WhiteoutNode(name)
        
        node = File(name, stats)
        #FIXME into constructor
        node.orig_inode = orig_stats.st_ino
        hl = hashlib.sha1()
        fobj = open(path, 'r')
        while True:
            data = fobj.read(16 * 4096)
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
            if (childname == '.wh..wh.orph'): continue
            if (childname == '.wh..wh.plnk'): continue

            childpath = subpath + '/' + childname
            child = _searchFiles(root, childpath, datastore, childname, unionfspath)
            child.addTo(node)

        return node

    if stat.S_ISBLK(stats.st_mode) or stat.S_ISCHR(stats.st_mode):
        dev = Device(name, stats)
        dev.rdev = orig_stats.st_rdev
        return dev

    if stat.S_ISFIFO(stats.st_mode):
        return FIFO(name, stats)

    
    return NullNode()
