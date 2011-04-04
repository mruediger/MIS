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
                current_root = current_root.children[name]
            except KeyError:
                return None

        return current_root

class Node(object):
    
    __slots__ = [ 
        "name",
        "stats"
    ]

        

    def __init__(self, name):
        self.name = name
        self.stats = dict()

class Directory(Node):

    __slots__ = Node.__slots__ + [ "children" ]

    def __init__(self, name=None):
        Node.__init__(self,name)
        self.children = dict()

    def is_directory(self):
        return True
        
    def addChild(self, child):
        self.children[child.name] = child 

class File(Node):
    
    __slots__ = Node.__slots__ + [ "hash" ]

    def __init__(self, name=None):
        Node.__init__(self,name)
        self.hash = None

    def is_directory(self):
        return False


