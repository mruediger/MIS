"""
mis.fs
======

provides the basic llfuse linkage
"""

import llfuse
import errno
import mis
import gzip

from collections import defaultdict

class Operations(llfuse.Operations):
    """The Operations class overloads llfuse.Operations where nessessary."""

    def __init__(self, manifest, datastore):
        self.manifest = manifest
        self.datastore = datastore
        
        self.nodecache  = [ None ] # inodes start with number 1
        self.entrycache = [ None ]

        self.hardlinks = dict()
	
        self.filecache = defaultdict(int)
	self.inode_open_count = defaultdict(int)

        self.fstat = llfuse.StatvfsData()
        #optimal transfer block size
        self.fstat.f_bsize = int(self.manifest.root.stats.st_blksize)
        #total data blocks in file system
        self.fstat.f_blocks = 0
        #free blocks in fs
        self.fstat.f_bfree = 0
        #free blocks available to unprivileged user
        self.fstat.f_bavail = 0
        #total file nodes in file system
        self.fstat.f_files = 0
        #free file nodes in fs
        self.fstat.f_ffree = 0
        self.fstat.f_favail = 0
        
        #fragment size
        self.fstat.f_frsize = int(self.manifest.root.stats.st_blksize)

        self.highest_inode = 1
        self.genEntryAndInode(manifest.root)

        for node in manifest:
            self.genEntryAndInode(node)

    def init(self):
        print "ready"

    def getattr(self, inode):
        return self.entrycache[inode]

    def genEntryAndInode(self, node):
        entry = llfuse.EntryAttributes()
        entry.attr_timeout  = 300
        entry.entry_timeout = 300
        entry.generation    = 1
        entry.st_rdev = node.rdev

        #metadata copy
        for attr in filter(lambda x: x.startswith('st_'), node.stats.__slots__):
            setattr(entry, attr, getattr(node.stats, attr))
    
        #hardlink detection
        if (isinstance(node, mis.manifest.nodes.File) and node.stats.st_nlink > 1):
            if(not self.hardlinks.has_key(node.orig_inode)):
                self.hardlinks[node.orig_inode] = self.highest_inode
            entry.st_ino = self.hardlinks[node.orig_inode]
        else:
            entry.st_ino  = self.highest_inode

        node.inode = self.highest_inode
        self.highest_inode += 1

        #update filesystem stats
        self.fstat.f_blocks += int(entry.st_blocks)
        self.fstat.f_files += 1

        self.entrycache.append( entry )
        self.nodecache.append( node )

    def opendir(self, inode):
        return inode

    def readdir(self, inode, off):
        for child in self.nodecache[inode]._children[off:]:
            off += 1
            yield(child.name, self.entrycache[child.inode], off)

    def lookup(self, parrent_ino, name):
        if name == '.':
            return self.entrycache[parrent_ino]
        if name == '..':
            parent = self.nodecache[parrent_ino].parent
            return self.entrycache[parent.inode]
        else:
            try:
                node = self.nodecache[parrent_ino].children_as_dict[name]
                return self.entrycache[node.inode]
            except KeyError:
                raise llfuse.FUSEError(errno.ENOENT)

    def forget(self, inode, lookup):
        pass

    def open(self, inode, flags):
        node = self.nodecache[inode]
        self.inode_open_count[inode] += 1
	if hasattr(node, "hash"):
           path = self.datastore.getPath(node)
       
           if self.datastore.is_compressed():
              self.filecache[inode] = gzip.open(path)
           else:
              self.filecache[inode] = open(path)
        return inode

    def read(self, fh, offset, length):
        if fh in self.filecache:
            self.filecache[fh].seek(offset)
            data = self.filecache[fh].read(length)
            return data
        else:
            return ""

    def release(self, fh):
        self.inode_open_count[fh] -= 1

        if self.inode_open_count[fh] == 0:
           del self.inode_open_count[fh]
           if fh in self.filecache:
              self.filecache[fh].close()
              del self.filecache[fh]

    def readlink(self, inode):
        return self.nodecache[inode].target

    def statfs(self):
        """Get file system statistics"""
        return self.fstat


#    def __getattribute__(self,name):
#        print name + " called"
#        return object.__getattribute__(self, name)
