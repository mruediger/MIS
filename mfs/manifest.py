import stat
import os

testvalue = 1

def searchFiles(path, name=""):
    if (not os.path.exists(path)):
        return

    if os.path.islink(path):
        node = SymbolicLink(name)
        setStats(node, os.lstat(path))
        return node

    if os.path.isfile(path):
        node = File(name)
        setStats(node, os.lstat(path))
        return node
        
    if os.path.isdir(path):
        node = Directory(name)
        for child in os.listdir(path):
            childpath = path + '/' + child
            node.children.append(searchFiles(childpath, child))
        return node

        
    
def setStats(node,stats):
    for key in [key for key in node.__slots__ if key.startswith("st_")]:
        setattr(node, key, getattr(stats, key))

class Manifest(object):

    __highest_inode = 0
    __hardlinked_inodes = dict()

    def __init__(self, root):
        self.root = root
        self.cache = list()

    def getNode(self, inode):
        if (inode == 1):
            return self.root

    def getNodeByInode(self, inode):
        pass #TODO

    def getNodeByPath(self, path):
        pass #TODO

    def genInode(self, inode=None):
        if (inode is not None):
            if (not __hardlinked_inodes.has_key(inode)):
                __highest_inode += 1
                __hardlinked_inodes[inode] = __highest_inode
            return __hardlinked_inodes[inode]
        else:
            __highest_inode += 1
            return __highest_inode
        


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
        'st_mode' ]

    def __init__(self, name):
        self.name = name
        
        # ACCESS
        self.st_ino  = 1 # inode number
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

    st_rdev = property(lambda self: 0)    

class Socket(Node):
    pass

class SymbolicLink(Node):
    pass

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
        self.children = list()
        self.st_mode = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                        stat.S_IRGRP | stat.S_IXGRP |
                        stat.S_IROTH | stat.S_IXOTH |
                        stat.S_IFDIR)

    def addChild(self, child, manifest, inode=None):
        self.children[inode] = child

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

    st_nlink = property(lambda self: testvalue)
