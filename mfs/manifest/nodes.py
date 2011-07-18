# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# Distributed under the terms of the GNU General Public License v2

"""manifest

the manifest object and the classes representing files"""

import stat
import os

from lxml import etree
from collections import deque
from mfs.exporter import *

class Manifest(object):

    def __init__(self, root):
        self.root = root

    def toXML(self):
        tree = etree.ElementTree(self.root.toXML())
        return tree

    def export(self, target, datastore, whiteouts=None):
        assert(os.path.isdir(target))
        if whiteouts == "unionfs":
            exporter = UnionFSExporter(target)
        elif whiteouts == "aufs":
            exporter = AUFSExporter(target)
        else:
            exporter = Exporter(target)
        self.root.export(datastore, exporter)

    def __eq__(self, manifest):
        return self.root == manifest.root

    def __iter__(self):
        for child in self.root:
            yield(child)

class Node(object):
    
    __slots__ = [
        'name',
        'inode',
        'st_uid',
        'st_gid',
        'st_blksize',   #TODO sparse files checken
        'st_size',      #TODO sparse files checken 
        'st_blocks',    #TODO sparse files checken
        'st_atime',
        'st_mtime',
        'st_ctime',
        'st_mode',
        'st_nlink', 
        'whiteout' ]

    def __init__(self, name, stats=None):
        if (name is None):
            raise ValueError
        self.name = name
        self.whiteout = False

        if stats is not None:
            for key in [key for key in self.__slots__ if key.startswith("st_")]:
                setattr(self, key, getattr(stats, key))
        
    def __str__(self):
        return self.name

    def __eq__(self, node):
        if self.__slots__ != node.__slots__:
            return False

        for key in self.__slots__:
            #inode is dynamic
            if (key == 'inode') : continue

            #children and whiteouts may differ in order
            if (key == '_children') : continue
            if (key == '_whiteouts') : continue

            #time may differ slightly
            if (key.endswith('time')) : continue
            if (hasattr(self, key) and hasattr(node, key)):
                if (getattr(self, key) != getattr(node, key)):
                    return False
            else:
                if (hasattr(self,key) != hasattr(node,key)):
                    return False
        return True
    
    def __iter__(self):
        yield self

    def __hash__(self):
        """because the merger needs set support"""
        return self.name.__hash__()

    def export(self, datastore, exporter):
        raise Exception("Node Objects cannot be exported")

    def addTo(self, directory):
        assert isinstance(directory, Directory)
        directory._children.append(self)

    def copy(self):
        retval = self.__new__(type(self), self.name)
        for key in self.__slots__:
            if hasattr(self, key):
                setattr(retval, key,getattr(self,key))
        return retval

    def toXML(self):
        xml = etree.Element("file")
        xml.attrib["name"] = self.name
        xml.attrib["type"] = type(self).__name__

        for key in filter(lambda x: x.startswith("st_"), self.__slots__):
            if not hasattr(self,key): continue
            attr = getattr(self,key)
            element = etree.SubElement(xml, key, type=type(attr).__name__)
            element.text = str(attr)
        return xml

    #only defined for special files
    st_rdev = property(lambda self: 0)

    def apply_stats(self, path):
        os.chown(path, self.st_uid, self.st_gid)        #TODO security
        os.utime(path, (self.st_atime, self.st_mtime))
        os.chmod(path, self.st_mode)                    #TODO security


class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    def toXML(self):
        xml = super(SymbolicLink,self).toXML()
        if hasattr(self, "target"):
           element = etree.SubElement(xml, "target", type="str")
           element.text = self.target
        return xml

    def export(self, datastore, exporter):
        try:
            os.symlink(self.target, exporter.getPath(self))
            self.apply_stats(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "symlink: {0}: {1}".format(exporter.getPath(self), strerror)
            return


class Device(Node):

    #the rest is handled automaticly by setStat
    __slots__ = Node.__slots__ + ['st_rdev']
    
    def export(self, datastore, exporter):
        try:
            os.mknod(exporter.getPath(self), self.st_mode, os.makedev(
                os.major(self.st_rdev),
                os.minor(self.st_rdev)
            ))
            self.apply_stats(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mknod: {0}: {1}".format(exporter.getPath(self), strerror)
            return

class FIFO(Node):

    def export(self, datastore, exporter):
        try:
            os.mkfifo(exporter.getPath(self))
            self.apply_stats(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mkfifo: {0}: {1}".format(exporter.getPath(self), strerror)
            return

class Directory(Node):

    __slots__ = Node.__slots__ + [ '_children', '_whiteouts'  ]
    
    def __init__(self, name, stats=None):
        Node.__init__(self,name, stats)
        self._children = list()
        self._whiteouts = list()
          
    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self._children + self._whiteouts:
            xml.append(child.toXML())
        return xml

    def copy(self):
        retval = super(Directory,self).copy()
        retval._children = list()
        return retval

    def export(self, datastore, exporter):
        try:
            os.mkdir(exporter.getPath(self))
            self.apply_stats(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mkdir {0}: {1}".format(exporter.getPath(self), strerror)

        olddir = exporter.directory
        exporter.directory = self.name

        for child in ( self._children + self._whiteouts ):
            child.export(datastore, exporter)

        exporter.directory = olddir #FIXME

    def __iter__(self):
        yield self
        for child in self._children:
            for retval in child:
                yield retval

    def __eq__(self, node):
        if (not super(Directory,self).__eq__(node)):
            return False
        else:
            if not (len(self._children) == len(node._children)):
                return False

            if not (len(self._whiteouts) == len(node._whiteouts)):
                print self._whiteouts
                print node._whiteouts
                return False

            ochildren = sorted(self._children, key=lambda child: child.name)
            nchildren = sorted(node._children, key=lambda child: child.name)
            
            for n in range(0, len(self._children)):
                if not ochildren[n] == nchildren[n]:
                    return False

            return True

    def __str__(self):
        retval = self.name
        for child in self._children:
            for string in str(child).splitlines():
                retval += '\n'
                retval += self.name + '/' + string
                asdf
                
        return retval

    children_as_dict = property(lambda self: dict( (child.name, child) for child in self._children ))

class File(Node):

    __slots__ = Node.__slots__ + [ 'hash', 'orig_inode' ]

    def toXML(self):
        xml = super(File,self).toXML()
        if hasattr(self, "orig_inode"):
            element = etree.SubElement(xml, "orig_inode", type="int")
            element.text = str(self.orig_inode)
        if hasattr(self, "hash"):
            element = etree.SubElement(xml, "hash", type="str")
            element.text = str(self.hash)
        return xml

    def export(self, datastore, exporter):
        if (self.st_nlink > 1):
            if (self.orig_inode in exporter.linkcache):
                os.link(exporter.linkcache[self.orig_inode], exporter.getPath(self))
                return
            else:
                exporter.linkcache[node.orig_inode] = exporter.getPath(self)

        source = datastore.getData(self)
        dest = file(exporter.getPath(self), 'w')
            
        buf = source.read(1024)
        while len(buf):
            buf = source.read(1024)
            dest.write(buf)

        source.close()
        dest.close()
        self.apply_stats(exporter.getPath(self))

class DeleteNode(object):
    __slots__ = [
        'name'
    ]

    def __init__(self, name):
        self.name = name

    def toXML(self):
        xml = etree.Element("file")
        xml.attrib["name"] = self.name
        xml.attrib["type"] = type(self).__name__
        return xml

    def __iter__(self):
        yield self

    def addTo(self, directory):
        assert isinstance(directory, Directory)
        directory._whiteouts.append(self)

    def __eq__(self, node):
        return isinstance(node ,DeleteNode) and (self.name == node.name)

    def __hash__(self):
        """because the merger needs set support"""
        return self.name.__hash__()
        
    def __str__(self):
        return "DeleteNode ({0})".format(self.name)
    
    def __init__(self, name):
        self.name = name

    def export(self, datastore, exporter):
        exporter.handleWhiteout(self) 
