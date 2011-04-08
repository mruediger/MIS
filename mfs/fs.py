"""
mfs.fs
======

provides the basic llfuse linkage
"""

import llfuse
import thread
import errno
import mfs

def toEntryAttribute(stat):
    """converts the generic stat object of a manifest to a generic attribute"""
    pass


class Operations(llfuse.Operations):
    """The Operations class overloads llfuse.Operations where nessessary."""

    def __init__(self, manifest):
        self.manifest = manifest
        
        self.dircache = dict ()
        self.dircache_lock = thread.allocate_lock()

        self.highest_inode = 1
        self.dircache[1] = manifest.root
        self.manifest.root.st_ino = 1
        

    def init(self):
        pass

    def getattr(self, inode):
        return self.getattrFromNode(self.dircache[inode])

    def getattrFromNode(self, node):
        entry = llfuse.EntryAttributes()

        #timeout for attributes in seconds
        entry.attr_timeout  = 10
        entry.entry_timeout = 10
        entry.generation    = 0

        if (node.st_ino is None):
            self.highest_inode += 1
            node.st_ino = self.highest_inode

        entry.st_ino     = node.st_ino
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

        if isinstance (node, mfs.manifest.Directory):
            with self.dircache_lock:
                self.dircache[node.st_ino] = node

        if isinstance (node, mfs.manifest.SymbolicLink):
            with self.dircache_lock:
                self.dircache[node.st_ino] = node

        return entry

    def forget(self, inode, lookup):
        try:
            del self.dircache[inode]
        except KeyError:
            pass

    def opendir(self, inode):
        return inode

    def relasedir(self, fh):
        del self.dircache[fh]

    def readdir(self, fh, off):
        for child in self.dircache[fh].children.values()[off:]:
            off += 1
            yield(child.name , self.getattrFromNode(child), off)

    def lookup(self, parrent_ino, name):
        if name == '.' or name == '..':
            return self.getattr(parrent_ino) #FIXME
        else:
            try:
                return self.getattrFromNode(self.dircache[parrent_ino].children[name])
            except KeyError:
                raise llfuse.FUSEError(errno.ENOENT)


    def readlink(self, inode):
        return self.dircache[inode].target
    
    def __getattribute__(self,name):
        #print name + " called"
        return object.__getattribute__(self, name)

