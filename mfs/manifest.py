import stat
import os

from lxml import etree
from collections import deque

def manifestFromPath(path, datastore=None):
    root = searchFiles(path, datastore, name='/')
    return Manifest(root)

def manifestFromXML(xml_file):

    #A stack with a dummy at the bottom
    parent = deque( [type('tmptype',(object,), dict(children=list()))] )

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
            mum.children.append(me)
            parent.append(mum)
            element.clear()
    
    return Manifest(parent.pop().children[0])

def searchFiles(path, datastore, name):
    if (not os.path.exists(path)):
        return

    stats = os.lstat(path)

    if stat.S_ISLNK(stats.st_mode):
        node = SymbolicLink(name, stats)
        node.target = os.readlink(path)
        return node

    if stat.S_ISREG(stats.st_mode):
        node = File(name, stats)
        node.orig_inode = stats.st_ino
        if (datastore is not None):
            datastore.saveData(node, path)
        return node
        
    if stat.S_ISDIR(stats.st_mode):
        node = Directory(name, stats)
        for child in os.listdir(path):
            childpath = path + '/' + child
            node.children.append(searchFiles(childpath, datastore, child))
        return node

    if stat.S_ISSOCK(stats.st_mode):
        node = Socket(name, stats)
        return node

    if stat.S_ISBLK(stats.st_mode):
        node = Device(name, stats)
        return node

    if stat.S_ISCHR(stats.st_mode):
        node = Device(name, stats)
        return node

    if stat.S_ISFIFO(stats.st_mode):
        node = FIFO(name, stats)
        return node

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

            #children may differ in order
            if (key == 'children') : continue

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

class Socket(Node):
    pass

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

    __slots__ = Node.__slots__ + [ 'children' ]
    
    def __init__(self, name, stats=None):
        Node.__init__(self,name, stats)
        self.children = list()
          
    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self.children:
            xml.append(child.toXML())
        return xml

    def copy(self):
        retval = super(Directory,self).copy()
        retval.children = list()
        return retval

    def children_as_dict(self):
        retval = dict()
        for child in self.children:
            retval[child.name] = child
        return retval

    def __iter__(self):
        yield self
        for child in self.children:
            for retval in child:
                yield retval

    def __eq__(self, node):
        if (not super(Directory,self).__eq__(node)):
            return False
        else:
            if not (len(node.children) == len(self.children)):
                return False

            for child in self.children:
                if not child in node.children:
                    return false
            
            return True

    def __str__(self):
        retval = self.name
        for child in self.children:
            for string in str(child).splitlines():
                retval += '\n'
                retval += self.name + '/' + string
        return retval

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
