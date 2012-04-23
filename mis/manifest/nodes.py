# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# Distributed under the terms of the GNU General Public License v2

"""manifest definition

the manifest object and the classes representing files"""

import stat
import os
import uuid

from copy import copy,deepcopy
from lxml import etree
from collections import deque

import mis.fileops
from mis.exporter import *


class Manifest(object):
    """  """
    def __init__(self, root):
        self.root = root
        self.uuid = str(uuid.uuid4())
        self._parents = list()

    def diff(self, manifest):
        """returns a string describing the differences of the
        given and actual manifest"""
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
                hashes.append( (hash,child.stats.st_size) )
        return hashes

    def __copy__(self):
        return Manifest(deepcopy(self.root))

    def __add__(self, manifest):
        """x.__add__(y) <==> x + y
        merges two virtual machine images"""
        new_root = self.root + manifest.root
        new_manifest = Manifest(new_root)
        new_manifest._parents.append(self.uuid)
        new_manifest._parents.append(manifest.uuid)
        return new_manifest


    def __sub__(self, manifest):
        """x.__sub__(y) <==> x - y
        returns a new manifest that only contains
        files in x that are not in y 
        ( only_update = update_image - orig_image"""
        new_root = self.root - manifest.root
        new_manifest = Manifest(new_root)
        new_manifest._parents.append(self.uuid)
        new_manifest._parents.append(manifest.uuid)
        return new_manifest

    def __eq__(self, manifest):
        """x.__eq__(y) <==> x==y""" 
        return self.root == manifest.root

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        for child in self.root:
            yield(child)

class Stats(object):
    """container for metadata information providet by the stat() call"""

    __slots__ = [
        'st_uid',
        'st_gid',
        'st_blksize',
        'st_size',
        'st_blocks',
        'st_atime',
        'st_mtime',
        'st_ctime',
        'st_mode',
        'st_nlink']
    
    def __init__(self, stats=None):
        for key in self.__slots__:
            setattr(self, key, copy(getattr(stats, key, None)))

    def __getstate__(self):
        """needed for pickle because of __slots__ usage"""
        return [ getattr(self, slot, None) for slot in self.__slots__ ]

    def __setstate__(self, state):
        """needed for pickle because of __slots__ usage"""
        for i in range(0, len(state)):
            setattr(self, self.__slots__[i], state[i])

    def __copy__(self):
        """x.__copy__() <==> copy(x)"""
        return Stats(self) 

    def __deepcopy__(self):
        """x.__deepcopy__() <==> deepcopy(x)"""
        return self.__copy__()

    def __eq__(self, stats):
        """x.__eq__(y) <==> x==y""" 
        slots = filter(lambda x: not x.endswith("time"), self.__slots__)
        return all([ getattr(self, slot, None) == getattr(stats, slot, None) for slot in slots ])

    def __str__(self):
        """x.__str__() <==> str(x)
        returns list of stats"""
        return str().join([slot + ":" + str(getattr(self,slot,None)) + '\n' for slot in self.__slots__])

    def isNewerThan(self, stats):
        """compares the files modification time."""
        # this method is used by __add__
        return self.st_mtime > stats.st_mtime 

    def toXML(self):
        xml = etree.Element("stats")
        for key in filter(lambda x: x.startswith("st_"), self.__slots__):
            if not hasattr(self,key): continue
            attr = getattr(self,key)
            element = etree.SubElement(xml, key, type=type(attr).__name__)
            element.text = str(attr)
        return xml
        
    def export(self, path):
        """changes uid, gid, mode, mtime and atime of the given file"""
        os.chown(path, self.st_uid, self.st_gid) 
        os.chmod(path, self.st_mode) 
        os.utime(path, (self.st_atime, self.st_mtime))

class Node(object):
    """abstract class which doesn't represent an existing file type"""

    __slots__ = [
        'name',
        'parent',
        'stats',
        'inode']

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
        if (name == ""):
            name = '/'
        self.name = name
        if not stats: stats = Stats()
        self.stats = stats
        self.parent = None

    def __getstate__(self):
        """needed for pickle because of __slots__ usage"""
        return [ getattr(self, slot, None) for slot in self.__slots__ ]

    def __setstate__(self, state):
        """needed for pickle because of __slots__ usage"""
        for i in range(0, len(state)):
            setattr(self, self.__slots__[i], state[i])
            
    def __add__(self, node):
        """Merge to Files"""
        if node.isNewerThan(self):
            return copy(node)
        else:
            return copy(self)

    def __sub__(self, node):
        """Delete File if content equals"""
        if (self == node): # only delete if nodes are exactly the same
            return None
        else:
            return copy(self)

    def diff(self, node):
        """returns a string describing the differences
        of the given and the actual stat object"""
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
        """x.___str___() <==> str(x)
        returns the path"""
        if (self.parent):
            return str(self.parent) + '/' + self.name
        else:
            return self.name

    def __eq__(self, node):
        """x.__eq__(y) <==> x==y
        compares filename, attributes and content"""
        
        for key in self.__slots__:
            #we do not want to loop endlessly
            if (key == 'parent') : continue

            #inode is dynamic
            if (key == 'inode') : continue

            #the order of [_children] may differ
            if (key == '_children') : continue

            if not getattr(self, key, None) == getattr(node, key, None):
                return False

        return True

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        yield self

    def __copy__(self):
        """clones the object"""
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
        """clones the object"""
        return self.__copy__()

    def isNewerThan(self, node):
        """compares the files modification time"""
        self.stats.isNewerThan(node.stats)

    def export(self, datastore, exporter):
        raise Exception("Node Objects cannot be exported")

    def remove(self, exporter):
        """removes the file on the filesystem"""
        os.remove(exporter.getPath(self))

    def addTo(self, directory):
        """insertes the file into a directory"""
        assert isinstance(directory, Directory)
        directory._children.append(self)
        self.parent = directory

    def toXML(self):
        xml = etree.Element("file")
	xml.attrib["name"] = self.name.decode('utf-8')
        xml.attrib["type"] = type(self).__name__
        xml.append(self.stats.toXML())
        return xml

    path = property(lambda self: getattr(self.parent, 'path', "") + self.name, 
        doc="the path in the image")
    rdev = property(lambda self: 0,
        doc="returns 0 since rdev only has a meaning for device files")

class SymbolicLink(Node):
    """class representing a symbolic link"""

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
        """creates a symbolic link under the path storend in the exporter object"""
        try:
            os.symlink(self.target, exporter.getPath(self))
            os.lchown(exporter.getPath(self), self.stats.st_uid, self.stats.st_gid)
        except OSError as (errno, strerror):
            #not a real error
            #print "symlink: {0}: {1}".format(exporter.getPath(self), strerror)
            return

class Device(Node):
    """class representing a device file"""

    #the rest is handled automaticly by setStat
    __slots__ = Node.__slots__ + ['rdev']
    
    def toXML(self):
        xml = super(Device, self).toXML()
        element = etree.SubElement(xml, "rdev", type="int")
        element.text = str(self.rdev)
        return xml

    def export(self, datastore, exporter):
        """creates a device file under the path storend in the exporter object"""
        if os.path.exists(exporter.getPath(self)):
            os.remove(exporter.getPath(self))
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
    """class representing a fifo"""

    def export(self, datastore, exporter):
        """creates a fifo under the path storend in the exporter object"""
        if os.path.exists(exporter.getPath(self)):
            os.remove(exporter.getPath(self))

        try:
            os.mkfifo(exporter.getPath(self))
            self.stats.export(exporter.getPath(self))
        except OSError as (errno, strerror):
            print "mkfifo: {0}: {1}".format(exporter.getPath(self), strerror)
            return

class Directory(Node):
    """class representing a directory"""

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
        """merges two directories"""

        if node.isNewerThan(self):
            #flat copy doesn't contain dir content
            retval = copy(node)
        else:
            retval = copy(self)

        if isinstance(node, WhiteoutNode):
            # break here when the dir was maked as deleted
            return retval

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
        """Returns a directory object that only contains the differences
        between x and y for x.__sub__(y). If a files are present in y but
        not in x, RMNodes are stored to allow for something like
        only_update = updated_image - orig_image, in a way that later merges
        will result in an updatet manifest 
        (orig_image + only_update = updated_image)"""

        if (self == node):
            # delete if there are no differences
            return None

        retval = copy(self)

        snodes = self.children_as_dict
        nnodes = node.children_as_dict


        nodenames = set( snodes.keys() + nnodes.keys() )

        for nodename in nodenames:
            snode = snodes.get(nodename, None)
            nnode = nnodes.get(nodename, None)
            

            if (snode and nnode):
                newchild = snode - nnode
            elif nnode:
                # if files where removed, create RMNodes
                # to apply these changes to existing
                # images
                newchild = RMNode(deepcopy(nnode))
            else:
                newchild = deepcopy(snode)

            if newchild: 
                #check for None which happens
                #if x == y during x.__sub__(y)
                newchild.addTo(retval)
        
        return retval

    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self._children:
            xml.append(child.toXML())
        return xml

    def export(self, datastore, exporter):
        """creates a directory under the path storend in the exporter object"""
        if not os.path.exists(exporter.getPath(self)): 
            os.mkdir(exporter.getPath(self))

        # poor mans pushd 
        olddir = exporter.directory
        exporter.directory = exporter.directory + '/' + self.name

        for child in self._children:
            child.export(datastore, exporter)
       
        # poor mans popd
        exporter.directory = olddir

        # set times and mode after files are put into it
        self.stats.export(exporter.getPath(self))

    def remove(self, exporter):
        """recursively deletes the directory and its contents"""
        for child in self._children:
            child.remove(exporter)

        os.rmdir(exporter.getPath(self))

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        yield self
        for child in self._children:
            for retval in child:
                yield retval

    def diff(self, directory):
        """returns a string describing the differences
        of the directory contents"""
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
        """x.__eq__(y) <==> x==y"""
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

    path = property(lambda self: getattr(self.parent, 'path', "") + self.name + '/',
        doc="same as node but for directories a '/' is appended")
    children_as_dict = property(lambda self: dict( (child.name, child) for child in self._children ),
        doc="shortcut for acces by filename")

class File(Node):
    """A Class representing a "regular" file that holds content. It is the
    only type that interacts with the datastore"""

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
        """copies the datastore content to the path storend in the exporter object"""
        if (self.stats.st_nlink > 1): #has hardlinks
            if (self.orig_inode in exporter.linkcache): # content already created
                if os.path.exists(exporter.getPath(self)):
                    os.remove(exporter.getPath(self))
                os.link(exporter.linkcache[self.orig_inode], exporter.getPath(self))
                return
            else:
                exporter.linkcache[self.orig_inode] = exporter.getPath(self)

        is_sparsefile = ( self.stats.st_size > 
            ( self.stats.st_blocks * self.stats.st_blksize ))

        mis.fileops.copy(datastore.getURL(self), exporter.getPath(self), 
            is_sparsefile, datastore.is_compressed(), self.stats.st_blksize, self.stats.st_size)

        self.stats.export(exporter.getPath(self))

class WhiteoutNode(Node):
    """A class representing Whiteout Files like AuFS' .wh.foo"""

    def __str__(self):
        """x.__str__() <==> str(x)
        returns path"""
        if (self.parent):
            return str(self.parent) + '/' + self.name + '(delnode)'
        else:
            return '/' + self.name + '(delnode)'

    def isNewerThan(self, node):
        # node + whiteout always returns a whiteout
        return True

    def __add__(self, node):
        # whiteout + node always returns the node
        return copy(node)

    def toXML(self):
        xml = super(WhiteoutNode,self).toXML()
        xml.attrib["name"] = self.name
        xml.attrib["type"] = "WhiteoutNode"
        return xml
    
    def export(self, datastore, exporter):
        """creates a whiteout file of a type specified by the exporter object"""
        exporter.handleWhiteout(self) 

class PatchNode(Node):
    """PatchNode is a decorator which changes the exported file content"""

    __slots__ = Node.__slots__ + [ "node","content" ]

    def __init__(self, node, content):        
        Node.__init__(self, node.name)
        self.node = node
        self.content = content # filled by Server

    def export(self, datastore, exporter):
        """stores content provided by a script at the location generated
        within the exporter opject"""
        with open(exporter.getPath(self.node),'wb') as fdst:
            fdst.write(self.content)

        fdst.close()
        

class RMNode(Node):
    """RMNode: remove node is a decorator to handle the state of removed files in a manifest 
    generated by manifest_a - manifest_b"""

    __slots__ = Node.__slots__ + [ "node" ]
    
    def __init__(self, node):
        Node.__init__(self, node.name)
        self.node = node

    def export(self, datastore, exporter):
        """deletes the file at the path storend in the exporter object"""
        if os.path.exists(exporter.getPath(self.node)):
            self.node.remove(exporter)
