import stat
import os

from lxml import etree
from collections import deque

def manifestFromPath(path, datastore=None):
    if (os.path.exists(path + '/.unionfs')):
        unionfspath = path + '/.unionfs'
        root = searchFiles(path, '', datastore, '/', unionfspath)
    else:
        root = searchFiles(path, '', datastore, '/')
    return Manifest(root)

def manifestFromXML(xml_file):

    #A stack with a dummy at the bottom
    parent = deque( [Directory("dummy")] )

    for action, element in etree.iterparse(xml_file, events=("start","end")):
        if (element.tag == "file" and action=="start"):
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

def searchFiles(root, subpath, datastore, name, unionfs=None):
    
    #the root + subpath split is needed for unionfs check
    path = root + subpath 
    assert(os.path.exists(path))

    stats = os.lstat(path)

    if stat.S_ISLNK(stats.st_mode):
        node = SymbolicLink(name, stats)
        node.target = os.readlink(path)
        return node

    if stat.S_ISREG(stats.st_mode):
        if unionfs and os.path.exists(unionfs + subpath):
            return DeleteNode(name)

        if name.startswith(".wh."):
            return DeleteNode(name[4:])
        
        node = File(name, stats)
        node.orig_inode = stats.st_ino
        if (datastore is not None):
            datastore.saveData(node, path)
        return node
        
    if stat.S_ISDIR(stats.st_mode):
        node = Directory(name, stats)
        for childname in os.listdir(path):
            childpath = subpath + '/' + childname
            if (childname == '.unionfs'): continue

            child = searchFiles(root, childpath, datastore, childname, unionfs)
            child.addTo(node)

        return node

    if stat.S_ISBLK(stats.st_mode):
        return Device(name, stats)

    if stat.S_ISCHR(stats.st_mode):
        return Device(name, stats)

    if stat.S_ISFIFO(stats.st_mode):
        return FIFO(name, stats)

class Manifest(object):

    def __init__(self, root):
        self.root = root

    def toXML(self):
        tree = etree.ElementTree(self.root.toXML())
        return tree

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
        'st_nlink', ]

    def __init__(self, name, stats=None):
        if (name is None):
            raise ValueError
        self.name = name

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

class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    def toXML(self):
        xml = super(SymbolicLink,self).toXML()
        if hasattr(self, "target"):
           element = etree.SubElement(xml, "target", type="str")
           element.text = self.target
        return xml

class Device(Node):

    #the rest is handled automaticly by setStat
    __slots__ = Node.__slots__ + ['st_rdev']

class FIFO(Node):
    pass

class Directory(Node):

    __slots__ = Node.__slots__ + [ '_children','_whiteouts' ]
    
    def __init__(self, name, stats=None):
        Node.__init__(self,name, stats)
        self._children = list()
        self._whiteouts = list()
          
    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self._children:
            xml.append(child.toXML())
        return xml

    def copy(self):
        retval = super(Directory,self).copy()
        retval._children = list()
        retval._whiteouts = list()
        return retval

    def __iter__(self):
        yield self
        for child in self._children:
            for retval in child:
                yield retval

    def __eq__(self, node):
        if (not super(Directory,self).__eq__(node)):
            return False
        else:
            if not (len(node._children) == len(self._children)):
                return False

            for child in self._children:
                if not child in node._children:
                    return False
            
            return True

    def __str__(self):
        retval = self.name
        for child in self._children:
            for string in str(child).splitlines():
                retval += '\n'
                retval += self.name + '/' + string
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

class DeleteNode(object):

    __slots__ = [
        '_name'
    ]

    def __init__(self, name):
        self._name = name

    def toXML(self):
        xml = etree.Element("file")
        xml.attrib["name"] = self.__name
        xml.attrib["type"] = type(self).__name__
        return xml

    def __iter__(self):
        yield self

    def addTo(self, directory):
        assert isinstance(directory, Directory)
        directory._whiteouts.append(self)

    def __eq__(self, node):
        return isinstance(node ,DeleteNode) and (self._name == node._name)

    name = property(lambda self: "delnode:" + self._name)

    def __hash__(self):
        """because the merger needs set support"""
        return self._name.__hash__()
        
        

    def __str__(self):
        return "DeleteNode ({0})".format(self._name)

