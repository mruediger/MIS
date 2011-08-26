# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# Distributed under the terms of the GNU General Public License v2

"""manifest

the manifest object and the classes representing files"""

import stat
import os
import uuid

from copy import copy,deepcopy
from lxml import etree
from collections import deque

import mfs.fileops
from mfs.exporter import *


class Manifest(object):

    def __init__(self, root):
        self.root = root
        self.uuid = str(uuid.uuid4())
        self._parents = list()

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

    def is_child_off(self, manifest):
        return manifest.uuid in self._parents

    def is_parent_off(self, manifest):
        return self.uuid in manifest._parents

    def node_by_path(self, path):
        node = self.root
        if (path.lstrip('/') == node.name):
            return node

        for path_elm in path.lstrip(self.root.name + '/').split('/'):
            try:
                node = node.children_as_dict[path_elm]
            except KeyError:
                return None

        return node

    def get_hashes(self):
        hashes = list()
        for child in self.root:
            hash = getattr(child, "hash", None)
            if hash:
                hashes.append(hash)
        return hashes

    def __copy__(self):
        return Manifest(deepcopy(self.root))

    def __add__(self, manifest):
        new_root = self.root + manifest.root
        new_manifest = Manifest(new_root)
        new_manifest._parents.append(self.uuid)
        new_manifest._parents.append(manifest.uuid)
        return new_manifest


    def __sub__(self, manifest):
        new_root = self.root - manifest.root
        new_manifest = Manifest(new_root)
        new_manifest._parents.append(self.uuid)
        new_manifest._parents.append(manifest.uuid)
        return new_manifest

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
            setattr(self, key, copy(getattr(stats, key, None)))

    def __copy__(self):
        return Stats(self) 

    def __deepcopy__(self):
        return self.__copy__()

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
        os.chmod(path, self.st_mode)                    #TODO security
        os.utime(path, (self.st_atime, self.st_mtime))

class Node(object):
    
    __slots__ = [
        'name',
        'parent',
        'stats']

    _diffignore = [
        'st_ctime',
        'st_atime',
        'stats',
        'parent',
        '_children',
        'orig_inode'
    ]

    def __init__(self, name, stats=None):
        if (name is None):
            raise ValueError
        self.name = name
        if not stats: stats = Stats()
        self.stats = stats
        self.parent = None

    def __getstate__(self):
        return [ getattr(self, slot, None) for slot in self.__slots__ ]

    def __setstate__(self, state):
        for i in range(0, len(state)):
            setattr(self, self.__slots__[i], state[i])
            
    def __add__(self, node):
        return copy(node)

    def __sub__(self, node):
        pass

    def diff(self, node):
        retval = list()
        for slot in self.__slots__:
            if (slot in self._diffignore): continue
            s = getattr(self, slot, None)
            n = getattr(node, slot, None)
            if (s != n):
                retval.append("{0} != {1} ({2}: {3},{4})".format(self, node, slot, s, n))

        for slot in self.stats.__slots__:
            s = getattr(self.stats, slot, None)
            n = getattr(node.stats, slot, None)
            if (slot in self._diffignore): continue
            if (slot.endswith('time')): 
                s = str(s)
                n = str(n)
            if (s != n):
                retval.append("{0} != {1} ({2}: {3},{4})".format(self, node, slot, s, n))
            
        return retval 
        
    def __str__(self):
        if (self.parent):
            return str(self.parent) + '/' + self.name
        else:
            return self.name

    def __eq__(self, node):

        for key in self.__slots__:
            #we do not want to loop endlessly
            if (key == 'parent') : continue

            #inode is dynamic
            if (key == 'inode') : continue

            #children may differ in order
            if (key == '_children') : continue

            #time may differ slightly
            if (key.endswith('time')) : continue
            if not getattr(self, key, None) == getattr(node, key, None):
                return False

        return True

    def __iter__(self):
        yield self

    def __copy__(self):
        retval = self.__class__(self.name)
        for key in self.__slots__:
            if (key == 'parent'):
                setattr(retval, key, None)
                continue
            if (key == '_children'): 
                setattr(retval, key, list())
                continue

            if hasattr(self, key):
                setattr(retval, key, copy(getattr(self,key)))

        return retval

    def __deepcopy__(self, memo):
        return self.__copy__()


    def export(self, datastore, exporter):
        raise Exception("Node Objects cannot be exported")

    def remove(self, exporter):
        os.remove(exporter.getPath(self))

    def addTo(self, directory):
        assert isinstance(directory, Directory)
        directory._children.append(self)
        self.parent = directory

    def toXML(self):
        xml = etree.Element("file")
        xml.attrib["name"] = self.name
        xml.attrib["type"] = type(self).__name__
        xml.append(self.stats.toXML())
        return xml

    path = property(lambda self: getattr(self.parent, 'path', "") + self.name)
    rdev = property(lambda self: 0)

class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    _diffignore = Node._diffignore + [
        'st_mtime'
    ]
    def toXML(self):
        xml = super(SymbolicLink,self).toXML()
        element = etree.SubElement(xml, "target", type="str")
        element.text = self.target
        return xml

    def export(self, datastore, exporter):
        try:
            os.symlink(self.target, exporter.getPath(self))
            os.lchown(exporter.getPath(self), self.stats.st_uid, self.stats.st_gid)
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

    __slots__ = Node.__slots__ + [ '_children' ]
    _diffignore = Node._diffignore + [
        'st_size',
        'st_blocks'
    ]
        
    
    def __init__(self, name, stats=None):
        Node.__init__(self,name, stats)
        self._children = list()

    def __getitem__(self, i):
        return self._children[i]    

    def __add__(self, node):
        #FIXME: itertools oder filter/map benutzen
        retval = copy(node)

        snodes = self.children_as_dict
        nnodes = node.children_as_dict

        nodenames = set( snodes.keys() + nnodes.keys() )


        for nodename in nodenames:
            snode = snodes.get(nodename, None)
            nnode = nnodes.get(nodename, None)

            if (snode and nnode):
                newchild = snodes[nodename] + nnodes[nodename]
            elif (nnode):
                newchild = deepcopy(nnode)
            else:
                newchild = deepcopy(snode)

            newchild.addTo(retval)

        return retval

    def __deepcopy__(self, memo):
        retval = self.__copy__()
        for child in self._children:
            deepcopy(child).addTo(retval)

        return retval

    def __copy__(self):
        retval = super(Directory,self).__copy__()
        return retval

    def __sub__(self, node):
        if (self == node):
            return None

        retval = copy(node)

        snodes = self.children_as_dict
        nnodes = node.children_as_dict


        nodenames = set( snodes.keys() + nnodes.keys() )

        for nodename in nodenames:
            snode = snodes.get(nodename, None)
            nnode = nnodes.get(nodename, None)
            

            if (snode and nnode):
                newchild = snode - nnode
            elif snode:
                newchild = RMNode(deepcopy(snode))

            if newchild:
                newchild.addTo(retval)
        
        return retval

    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self._children:
            xml.append(child.toXML())
        return xml

    def export(self, datastore, exporter):
        try:
            os.mkdir(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mkdir {0}: {1}".format(exporter.getPath(self), strerror)

        olddir = exporter.directory
        exporter.directory = exporter.directory + '/' + self.name

        for child in self._children:
            child.export(datastore, exporter)
        
        exporter.directory = olddir #FIXME

        #set times and mode after files are put into it
        self.stats.export(exporter.getPath(self))

    def remove(self, exporter):
        for child in self._children:
            child.remove(exporter)

        os.rmdir(exporter.getPath(self))

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

            ochildren = sorted(self._children, key=lambda child: child.name)
            nchildren = sorted(node._children, key=lambda child: child.name)
            
            for n in range(0, len(self._children)):
                if not ochildren[n] == nchildren[n]:
                    return False
            

        return True

    path = property(lambda self: getattr(self.parent, 'path', "") + self.name + '/')
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

        sparsefile = ( self.stats.st_size > 
            ( self.stats.st_blocks * self.stats.st_blksize ))

        mfs.fileops.copy(datastore.getURL(self), exporter.getPath(self), 
            sparsefile, self.stats.st_blksize, self.stats.st_size)

        self.stats.export(exporter.getPath(self))

class DeleteNode(Node):
    #TODO rename to whiteout node

    __slots__ = [
        'name',
        'parent'
    ]
    
    def __str__(self):
        if (self.parent):
            return str(self.parent) + '/' + self.name + '(delnode)'
        else:
            return '/' + self.name + '(delnode)'
    
    def export(self, datastore, exporter):
        exporter.handleWhiteout(self) 

class PatchNode(Node):
    """PatchNode is a decorator with which the exported file content is changed
    during export time"""

    __slots__ = Node.__slots__ + [ "node","content" ]

    def __init__(self, node, content):
        Node.__init__(self, node.name)
        self.node = node
        self.content = content

    def export(self, datastore, exporter):
        with open(exporter.getPath(self.node),'wb') as fdst:
            fdst.write(self.content)

        fdst.close()
        

class RMNode(Node):
    """RMNode: remove node is a ??? to handle the state of removed files in a manifest 
    generated by manifest_a - manifest_b"""

    __slots__ = Node.__slots__ + [ "node" ]
    
    def __init__(self, node):
        Node.__init__(self, node.name)
        self.node = node

    def export(self, datastore, exporter):
        if os.path.exists(exporter.getPath(self.node)):
            self.node.remove(exporter)
