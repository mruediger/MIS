"""manifest - represents an image
"""

import uuid

class Manifest():
    
    def __init__(self, root):
        self.root = root
    
    def getPath(self, path):
        pathelements = path.split('/') 
        if (self.root.name == path):
            return self.root

        current_root = self.root

        for name in pathelements[1:]:
            #skip trailing '/'
            if name is '': continue

            try:
                current_root = current_root.getChild(name)
            except KeyError:
                return None

        return current_root

class Node(object):
    
    __slots__ = [ 
        "name",
        "sibling",
        "stats"
    ]

    def __getstate__ (self):
        return [getattr(self, attr) for attr in self.__slots__]


    def __init__(self, name):
        self.name = name
        self.sibling = None
        self.stats = None

    def getSiblings(self):
        sibling = self
        while sibling is not None:
            yield sibling
            sibling = sibling.sibling

class Directory(Node):

    __slots__ = Node.__slots__ + [ "child" ]

    def __init__(self, name=None):
        Node.__init__(self,name)
        self.child = None

    def __getstate__ (self):
        return [getattr(self, attr) for attr in self.__slots__]

    def is_directory(self):
        return True
        
    def addChild(self, child):
        if (self.child is None):
            self.child = child
        else:
            sibling = self.child
            while sibling.sibling is not None:
                sibling = sibling.sibling
            sibling.sibling = child

    def getChild(self, name):
        for child in self.child.getSiblings():
            if (name == child.name):
                return child
        return None

class File(Node):
    
    __slots__ = Node.__slots__ + [ "hash" ]

    def __getstate__ (self):
        return [getattr(self, attr) for attr in self.__slots__]

    def __init__(self, name=None):
        Node.__init__(self,name)
        self.hash = None

    def is_directory(self):
        return False


