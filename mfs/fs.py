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

    def __init__(self, manifest, datastore):
        self.manifest = manifest
        self.datastore = datastore
        
        self.inodecache = dict ()
        self.inodecache_lock = thread.allocate_lock()

        self.filecache = dict ()
        self.filecache_lock = thread.allocate_lock()

        self.highest_inode = 1
        self.inodecache[1] = manifest.root
        self.manifest.root.inode = 1
        
        self.hardlinks = dict()

    def init(self):
        pass

    def getattr(self, inode):
        return self.getattrFromNode(self.inodecache[inode])

    def getattrFromNode(self, node):
        entry = llfuse.EntryAttributes()

        #timeout for attributes in seconds
        entry.attr_timeout  = 10
        entry.entry_timeout = 10
        entry.generation    = 0

        if (not hasattr(node, "inode") or node.inode is None):
            if (isinstance(node, mfs.manifest.File) and node.st_nlink > 1):
                if(not self.hardlinks.has_key(node.orig_inode)):
                    self.highest_inode += 1
                    self.hardlinks[node.orig_inode] = self.highest_inode
                node.inode = self.hardlinks[node.orig_inode]
            else:
                self.highest_inode += 1
                node.inode = self.highest_inode

        entry.st_ino     = node.inode
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

        with self.inodecache_lock:
            self.inodecache[node.inode] = node

        return entry

    def forget(self, inode, lookup):
        try:
            del self.inodecache[inode]
        except KeyError:
            pass

    def opendir(self, inode):
        return inode

    def relasedir(self, fh):
        del self.inodecache[fh]

    def readdir(self, fh, off):
        for child in self.inodecache[fh].children[off:]:
            off += 1
            yield(child.name , self.getattrFromNode(child), off)

    def lookup(self, parrent_ino, name):
        if name == '.' or name == '..':
            return self.getattr(parrent_ino) #FIXME
        else:
            try:
                return self.getattrFromNode(self.inodecache[parrent_ino].children_as_dict[name])
            except KeyError:
                raise llfuse.FUSEError(errno.ENOENT)

    def open(self, inode, flags):
        with self.filecache_lock:
            self.filecache[inode] = self.datastore.getData(
                self.inodecache[inode]
            )
        return inode

    def read(self, fh, offset, length):
        self.filecache[fh].seek(offset)
        return self.filecache[fh].read(length)

    def release(self, fh):
        self.filecache[fh].close()
        del self.filecache[fh]

    def readlink(self, inode):
        return self.inodecache[inode].target
    
    def __getattribute__(self,name):
        #print name + " called"
        return object.__getattribute__(self, name)

