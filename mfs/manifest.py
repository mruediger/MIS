import stat
import os

testvalue = 1

def searchFiles(path, name=""):
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
        return node
        
    if os.path.isdir(path):
        node = Directory(name)
        setStats(node, os.lstat(path))
        for child in os.listdir(path):
            childpath = path + '/' + child
            node.children[child] = searchFiles(childpath, child)
        return node

        
    
def setStats(node,stats):
    for key in [key for key in node.__slots__ if key.startswith("st_")]:
        if key == "st_ino": continue
        setattr(node, key, getattr(stats, key))

class Manifest(object):

    def __init__(self, root):
        self.root = root

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
        self.name = name
        
        # ACCESS
        self.st_ino  = None 
        self.st_uid  = 0 # default to root
        self.st_gid  = 0 # default to root

        # SIZE
        self.st_blksize = 4096
        self.st_size    = 4096
        self.st_blocks  = 8     # number of 512B blocks allocated
        
        # TIME      
        self.st_atime = 0 # time of last access
        self.st_mtime = 0 # time of last modification
        self.st_ctime = 0 # time of last status change

        # MODE (to be set in file/directory)
        self.st_mode = 0

    def __str__(self):
        return self.name

    st_nlink = property(lambda self: 1)

class Socket(Node):
    pass

class SymbolicLink(Node):

    __slots__ = Node.__slots__ + [ 'target' ]

    def __init__(self, name):
        Node.__init__(self,name)
        

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
        self.st_mode = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                        stat.S_IRGRP | stat.S_IXGRP |
                        stat.S_IROTH | stat.S_IXOTH |
                        stat.S_IFDIR)

    def get_nlink(self):
        """ return the number of children """
        return len(children)

    def __str__(self):
        retval = self.name
        for child in self.children:
            for string in str(child).splitlines():
                retval += '\n'
                retval += self.name + '/' + string
        return retval

    #TODO: st_nlink sollte anzahl der verzeichnisse sein
    st_nlink = property(lambda self: len(self.children) + 2)

class File(Node):

    def __init__(self, name):
        Node.__init__(self,name)
        self.st_mode = (stat.S_IRUSR | stat.S_IWUSR | 
                        stat.S_IRGRP | 
                        stat.S_IROTH | 
                        stat.S_IFREG)

    st_nlink = property(lambda self: 1)
