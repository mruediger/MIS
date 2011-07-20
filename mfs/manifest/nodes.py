# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# Distributed under the terms of the GNU General Public License v2

"""manifest

the manifest object and the classes representing files"""

import stat
import os
import copy

from lxml import etree
from collections import deque
from mfs.exporter import *

class Manifest(object):

    def __init__(self, root):
        self.root = root

    def diff(self, manifest):
        return self.root.diff(manifest.root)

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

class Stats(object):

    __slots__ = [
        'st_uid',
        'st_gid',
        'st_blksize',   #TODO sparse files checken
        'st_size',      #TODO sparse files checken 
        'st_blocks',    #TODO sparse files checken
        'st_atime',
        'st_mtime',
        'st_ctime',
        'st_mode',
        'st_nlink' ]
    
    def __getstate__(self):
        return [ getattr(self, slot, None) for slot in self.__slots__ ]

    def __setstate__(self, state):
        for i in range(0, len(state)):
            setattr(self, self.__slots__[i], state[i])

    def __init__(self, stats=None):
        for key in self.__slots__:
            setattr(self, key, copy.copy(getattr(stats, key, None)))

    def __copy__(self):
        return Stats(self) 

    def __eq__(self, stats):
        slots = filter(lambda x: not x.endswith("time"), self.__slots__)
        return all([ getattr(self, slot, None) == getattr(stats, slot, None) for slot in slots ])

    def __str__(self):
        return str().join([slot + ":" + str(getattr(self,slot,None)) + '\n' for slot in self.__slots__])

    def toXML(self):
        xml = etree.Element("stats")
        for key in filter(lambda x: x.startswith("st_"), self.__slots__):
            if not hasattr(self,key): continue
            attr = getattr(self,key)
            element = etree.SubElement(xml, key, type=type(attr).__name__)
            element.text = str(attr)
        return xml
        
    def export(self, path):
        os.chown(path, self.st_uid, self.st_gid)        #TODO security
        os.utime(path, (self.st_atime, self.st_mtime))
        os.chmod(path, self.st_mode)                    #TODO security

class Node(object):
    
    __slots__ = [
        'name',
        'parent',
        'stats' ]

    def __getstate__(self):
        return [ getattr(self, slot, None) for slot in self.__slots__ ]

    def __setstate__(self, state):
        for i in range(0, len(state)):
            setattr(self, self.__slots__[i], state[i])
            

    def diff(self, node):
        retval = list()
        for slot in self.__slots__:
            if (slot == 'stats') : continue
            if (slot == 'parent') : continue
            if (slot == '_children') : continue
            s = getattr(self, slot, None)
            n = getattr(node, slot, None)
            if (s != n):
                retval.append("{0} != {1} ({2}: {3},{4})".format(self, node, slot, s, n))

        for slot in self.stats.__slots__:
            if (slot.endswith('time')) : continue
            s = getattr(self.stats, slot, None)
            n = getattr(node.stats, slot, None)
            if (s != n):
                retval.append("{0} != {1} ({2}: {3},{4})".format(self, node, slot, s, n))
            
        return retval 

    def __init__(self, name, stats=None):
        if (name is None):
            raise ValueError
        self.name = name
        if not stats: stats = Stats()
        self.stats = stats
        self.parent = None
        
    def __str__(self):
        if (self.parent):
            return str(self.parent) + '/' + self.name
        else:
            return '/' + self.name

    def __eq__(self, node):

        for key in self.__slots__:
            #we do not want to loop endlessly
            if (key == 'parent') : continue

            #inode is dynamic
            if (key == 'inode') : continue

            #children and whiteouts may differ in order
            if (key == '_children') : continue
            if (key == '_whiteouts') : continue

            #time may differ slightly
            if (key.endswith('time')) : continue
            if not getattr(self, key, None) == getattr(node, key, None):
                return False

        return True

    def toPath(self):
        if (self.parent):
            return self.parent.path + '/' + self.name
        else:
            return self.name
    
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
        self.parent = directory

    def copy(self):
        retval = self.__new__(type(self), self.name)
        for key in self.__slots__:
            if hasattr(self, key):
                setattr(retval, key, copy.copy(getattr(self,key)))
        

        return retval

    def toXML(self):
        xml = etree.Element("file")
        xml.attrib["name"] = self.name
        xml.attrib["type"] = type(self).__name__
        xml.append(self.stats.toXML())
        return xml

    path = property(lambda self: self.toPath())

class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    def toXML(self):
        xml = super(SymbolicLink,self).toXML()
        element = etree.SubElement(xml, "target", type="str")
        element.text = self.target
        return xml

    def export(self, datastore, exporter):
        try:
            os.symlink(self.target, exporter.getPath(self))
        except OSError as (errno, strerror):
            #not a real error
            #print "symlink: {0}: {1}".format(exporter.getPath(self), strerror)
            return


class Device(Node):

    #the rest is handled automaticly by setStat
    __slots__ = Node.__slots__ + ['rdev']
    
    def toXML(self):
        xml = super(Device, self).toXML()
        element = etree.SubElement(xml, "rdev", type="int")
        element.text = str(self.rdev)
        return xml

    def export(self, datastore, exporter):
        try:
            os.mknod(exporter.getPath(self), self.stats.st_mode, os.makedev(
                os.major(self.rdev),
                os.minor(self.rdev)
            ))
            self.stats.export(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mknod: {0}: {1}".format(exporter.getPath(self), strerror)
            return

class FIFO(Node):

    def export(self, datastore, exporter):
        try:
            os.mkfifo(exporter.getPath(self))
            self.stats.export(exporter.getPath(self))
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
            self.stats.export(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mkdir {0}: {1}".format(exporter.getPath(self), strerror)

        olddir = exporter.directory
        exporter.directory = exporter.directory + '/' + self.name

        for child in ( self._children + self._whiteouts ):
            child.export(datastore, exporter)

        exporter.directory = olddir #FIXME

    def __iter__(self):
        yield self
        for child in self._children:
            for retval in child:
                yield retval

    def diff(self, directory):
        retval = super(Directory, self).diff(directory)

        sdict = self.children_as_dict
        ndict = directory.children_as_dict

        for key in set(sdict.keys() + ndict.keys()):
            if (not key in sdict):
                retval.append("{0} only in {1} (<)".format(key, str(self)))
                continue
            if (not key in ndict):
                retval.append("{0} only in {1} (>)".format(key, str(directory)))
                continue
            retval += sdict[key].diff(ndict[key])
        
        return retval


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

    children_as_dict = property(lambda self: dict( (child.name, child) for child in self._children ))

class File(Node):

    __slots__ = Node.__slots__ + [ 'hash', 'orig_inode' ]

    def __init__(self, name, stats=None):
        Node.__init__(self,name,stats)
        self.hash = None

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
        if (self.stats.st_nlink > 1):
            if (self.orig_inode in exporter.linkcache):
                os.link(exporter.linkcache[self.orig_inode], exporter.getPath(self))
                return
            else:
                exporter.linkcache[self.orig_inode] = exporter.getPath(self)

        source = datastore.getData(self)
        dest = file(exporter.getPath(self), 'wb')

        #sparsefile handling from a shautil patch
        while True:
            buf = source.read(16*4096)
            if not buf:
                break
            if sparsefile and buf == '\0'*len(buf):
                dest.seek(len(buf), os.SEEK_CUR)
            else:
                dest.write(buf)

        dest.truncate(self.stats.st_size)
        dest.close()
        source.close()
        self.stats.export(exporter.getPath(self))

class DeleteNode(object):
    __slots__ = [
        'name',
        'parent'
    ]

    def __init__(self, name):
        self.name = name
        self.parent = None

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
        self.parent = directory

    def __eq__(self, node):
        return isinstance(node ,DeleteNode) and (self.name == node.name)

    def __hash__(self):
        """because the merger needs set support"""
        return self.name.__hash__()
        
    def __str__(self):
        if (self.parent):
            return str(self.parent) + '/' + self.name + '(delnode)'
        else:
            return '/' + self.name + '(delnode)'
    
    def __init__(self, name):
        self.name = name

    def export(self, datastore, exporter):
        exporter.handleWhiteout(self) 
