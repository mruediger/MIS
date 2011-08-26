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
        
        self.inodecache = dict ()

        self.filecache = dict ()

        self.highest_inode = 1
        self.setNodeAttr(manifest.root)
        self.inodecache[1] = manifest.root
        
        self.hardlinks = dict()

    def init(self):
        pass

    def getattr(self, inode):
        return self.inodecache[inode].entry

    def setNodeAttr(self, node):
        if (isinstance(node, mfs.manifest.nodes.File) and node.stats.st_nlink > 1):
            if(not self.hardlinks.has_key(node.orig_inode)):
                self.highest_inode += 1
                self.hardlinks[node.orig_inode] = self.highest_inode
            inode = self.hardlinks[node.orig_inode]
        else:
            self.highest_inode += 1
            inode = self.highest_inode

        entry = llfuse.EntryAttributes()
        entry.attr_timeout  = 300
        entry.entry_timeout = 300
        entry.generation    = 0
        entry.st_ino  = inode
        entry.st_rdev = node.rdev

        for attr in filter(lambda x: x.startswith('st_'), node.stats.__slots__):
            setattr(entry, attr, getattr(node.stats, attr))


        node.entry = entry
        
        self.inodecache[inode] = node

    def forget(self, inode, lookup):
        pass

    def opendir(self, inode):
        return inode

    def relasedir(self, fh):
        pass

    def readdir(self, fh, off):
        for child in self.inodecache[fh]._children[off:]:
            off += 1
            if not child.entry:
                self.setNodeAttr(child)

            yield(child.name, child.entry, off)

    def lookup(self, parrent_ino, name):
        if name == '.' or name == '..':
            return self.getattr(parrent_ino) #FIXME
        else:
            try:
                node = self.inodecache[parrent_ino].children_as_dict[name]
                if not node.entry:
                    self.setNodeAttr(node)
                return node.entry
            except KeyError:
                raise llfuse.FUSEError(errno.ENOENT)

    def open(self, inode, flags):
        if hasattr(self.inodecache[inode], "hash"):
            self.filecache[inode] = open(self.datastore.toPath(
                self.inodecache[inode].hash
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
        return self.inodecache[inode].target
    
    def __getattribute__(self,name):
        #print name + " called"
        return object.__getattribute__(self, name)

