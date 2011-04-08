"""
mfs.fs
======

provides the basic llfuse linkage
"""

import llfuse
import thread

def toEntryAttribute(stat):
    """converts the generic stat object of a manifest to a generic attribute"""
    pass


class Operations(llfuse.Operations):
    """The Operations class overloads llfuse.Operations where nessessary."""

    __highest_inode = 0
    __hardlinked_inodes = dict()

    #TODO nur einmal aufrufen lassen !
    def setInode(self, node):
        if hasattr(node, 'inode') and node.inode is None:
            return
        if node.is_hardlink:
            if (not __hardlinked_inodes.has_key(node.hash)):
                __highest_inode +=1
                __hardlinked_inodes[node.hash] = __highest_inode
            node.inode = __hardlinked_inodes[inode]
        else:
            __highest_inode += 1
            node.inode = __highest_inode
            


    def __init__(self, manifest):
        self.manifest = manifest
        self.cache = list()
        self.cache_lock = thread.allocate_lock()

    def init(self):
        pass

    def getattr(self, inode):
        if (inode == 1):
            return self.getattrFromNode(self.manifest.root)

    def getattrFromNode(self, node):
        entry = llfuse.EntryAttributes()

        #timeout for attributes in seconds
        entry.attr_timeout = 1 

        entry.st_ino     = inode
        entry.st_mode    = node.st_mode
        entry.st_nlink   = node.st_nlink
        entry.st_uid     = node.st_uid
        entry.st_gid     = node.st_gid
        entry.st_rdev    = node.st_rdev
        entry.st_size    = node.st_size
        entry.st_blksize = node.st_blksize
        entry.st_blocks  = node.st_blocks
        entry.st_atime   = node.st_atime
        entry.st_ctime   = node.st_ctime
        entry.st_mtime   = node.st_mtime
        return entry

    
    def opendir(self, inode):
        node = None
        retval = None
        if (inode == 1):
            node = self.manifest.root

        with self.cache_lock:
            self.cache.append(node)
            retval = len(self.cache) - 1
            
        return retval

    def readdir(self, fh, off):
        child = self.cache[fh].children[off]
        off += 1
        return child.name , self.getattrFromNode(child), off
    
    def __getattribute__(self,name):
        print name + " called"
        #return llfuse.Operations.__getattribute__(self, name)
        return object.__getattribute__(self, name)

