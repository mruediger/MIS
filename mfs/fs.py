"""
mfs.fs
======

provides the basic llfuse linkage
"""

import llfuse
import errno
import mfs


class Operations(llfuse.Operations):
    """The Operations class overloads llfuse.Operations where nessessary."""

    def __init__(self, manifest, datastore):
        self.manifest = manifest
        self.datastore = datastore
        
        self.nodecache  = [ None ] # inodes start with number 1
        self.entrycache = [ None ]

        self.filecache = dict()
        self.hardlinks = dict()

        self.highest_inode = 1
        self.genEntryAndInode(manifest.root)

        for node in manifest:
            self.genEntryAndInode(node)

    def init(self):
        pass

    def getattr(self, inode):
        return self.entrycache[inode]

    def genEntryAndInode(self, node):
        entry = llfuse.EntryAttributes()
        entry.attr_timeout  = 300
        entry.entry_timeout = 300
        entry.generation    = 0
        entry.st_rdev = node.rdev

        for attr in filter(lambda x: x.startswith('st_'), node.stats.__slots__):
            setattr(entry, attr, getattr(node.stats, attr))

        if (isinstance(node, mfs.manifest.nodes.File) and node.stats.st_nlink > 1):
            if(not self.hardlinks.has_key(node.orig_inode)):
                self.hardlinks[node.orig_inode] = self.highest_inode
            entry.st_ino = self.hardlinks[node.orig_inode]
        else:
            entry.st_ino  = self.highest_inode

        node.inode = self.highest_inode
        self.highest_inode += 1

        self.entrycache.append( entry )
        self.nodecache.append( node )

    def opendir(self, inode):
        return inode

    def readdir(self, inode, off):
        for child in self.nodecache[inode]._children[off:]:
            off += 1
            yield(child.name, self.entrycache[child.inode], off)

    def lookup(self, parrent_ino, name):
        if name == '.' or name == '..':
            return self.getattr(parrent_ino) #FIXME
        else:
            try:
                node = self.nodecache[parrent_ino].children_as_dict[name]
                return self.entrycache[node.inode]
            except KeyError:
                raise llfuse.FUSEError(errno.ENOENT)

    def open(self, inode, flags):
        node = self.nodecache[inode]
        if hasattr(node, "hash"):
            self.filecache[inode] = open(self.datastore.toPath(
                node.hash
            ))
        return inode

    def read(self, fh, offset, length):
        if fh in self.filecache:
            self.filecache[fh].seek(offset)
            return self.filecache[fh].read(length)
        else:
            return ""

    def release(self, fh):
        if fh in self.filecache:
            self.filecache[fh].close()
            del self.filecache[fh]

    def readlink(self, inode):
        return self.nodecache[inode].target
