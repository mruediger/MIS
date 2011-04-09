import stat
import os

from lxml import etree
from collections import deque


def manifestFromPath(path, datastore=None):
    root = searchFiles(path, datastore, name='/')
    return Manifest(root)

def manifestFromXML(xml_file):

    #A stack with a dummy at the bottom
    parent = deque( [type('tmptype',(object,), dict(children=dict()))] )

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

        if (element.tag == "target" and action=="end"):
            parent[len(parent) - 1].target = element.text
            
        #because root will get removed to, we need a dummy
        if (element.tag == "file" and action=="end"):
            me = parent.pop() 
            mum = parent.pop()
            mum.children[me.name] = me
            parent.append(mum)
            element.clear()
    
    return Manifest(parent.pop().children.values()[0])
    
def searchFiles(path, datastore, name):
    if (not os.path.exists(path)):
        return

    if os.path.islink(path):
        node = SymbolicLink(name)
        setStats(node, os.lstat(path))
        node.target = os.readlink(path)
        return node

    if os.path.isfile(path):
        node = File(name)
        setStats(node, os.lstat(path))
        if (datastore is not None):
            datastore.saveData(node, path)

        return node
        
    if os.path.isdir(path):
        node = Directory(name)
        setStats(node, os.lstat(path))
        for child in os.listdir(path):
            childpath = path + '/' + child
            node.children[child] = searchFiles(childpath, datastore, child)
        return node

def setStats(node,stats):
    for key in [key for key in node.__slots__ if key.startswith("st_")]:
        if key == "st_ino": continue
        setattr(node, key, getattr(stats, key))

class Manifest(object):

    def __init__(self, root):
        self.root = root

    def toXML(self):
        tree = etree.ElementTree(self.root.toXML())
        return tree


class Node(object):
    
    __slots__ = [
        'name',
        'st_ino',
        'st_uid',
        'st_gid',
        'st_blksize',
        'st_size',
        'st_blocks',
        'st_atime',
        'st_mtime',
        'st_ctime',
        'st_mode',
        'st_rdev' ]

    def __init__(self, name):
        if (name is None):
            raise ValueError
        self.name = name
        
    def __str__(self):
        return self.name

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


    st_nlink = property(lambda self: 1)

class Socket(Node):
    pass

class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    def __init__(self, name):
        Node.__init__(self,name)
        
    def toXML(self):
        xml = super(SymbolicLink,self).toXML()
        if hasattr(self, "target"):
           element = etree.SubElement(xml, "target", type="str")
           element.text = self.target
        return xml

class BlockDevice(Node):
    pass

class CharacterDevice(Node):
    pass

class FIFO(Node):
    pass

class Directory(Node):

    __slots__ = Node.__slots__ + [ 'children' ]
    
    def __init__(self, name):
        Node.__init__(self,name)
        self.children = dict()
          
    def toXML(self):
        xml = super(Directory,self).toXML()
        for child in self.children.values():
            xml.append(child.toXML())
        return xml

    def __str__(self):
        retval = self.name
        for child in self.children:
            for string in str(child).splitlines():
                retval += '\n'
                retval += self.name + '/' + string
        return retval

    st_nlink = property(lambda self: len(self.children) + 2)

class File(Node):

    __slots__ = Node.__slots__ + [ 'hash' ]

    def __init__(self, name):
        Node.__init__(self,name)

    def toXML(self):
        xml = super(File,self).toXML()
        if hasattr(self, "hash"):
           element = etree.SubElement(xml, "hash", type="str")
           element.text = self.hash
        return xml

        
    st_nlink = property(lambda self: 1)
