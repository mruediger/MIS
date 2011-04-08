"""
mfs.fs
======

provides the basic llfuse linkage
"""

import llfuse


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

    def init(self):
        pass

    def getattr(self, inode):
        entry = llfuse.EntryAttributes()

        #timeout for attributes in seconds
        entry.attr_timeout = 1 

        entry.st_ino     = inode
        entry.st_mode    = 16887
        entry.st_nlink   = 2
        entry.st_uid     = 1000
        entry.st_gid     = 1000
        entry.st_rdev    = 0
        entry.st_size    = 4096
        entry.st_blksize = 4096
        entry.st_blocks  = 8
        entry.st_atime   = 1301940008
        entry.st_ctime   = 1301940008
        entry.st_mtime   = 1301940008
        return entry

    def opendir(self, inode):
        return 123

    def readdir(self, fh, off):
        print fh
        return []
    
    def __getattribute__(self,name):
        print name + " called"
        #return llfuse.Operations.__getattribute__(self, name)
        return object.__getattribute__(self, name)

