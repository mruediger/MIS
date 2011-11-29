# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

import os
import tempfile
from urlparse import urlparse, urlsplit, urljoin

import fileops
import gzip

class Datastore(object):

    SPARSE = 1
    GZIP1  = 2
    GZIP6  = 3

    def __init__(self, url, storetype):
        if (url[-1] != '/'):
            url = url + '/'
        self.url = urlparse(url, 'file')
        self.path = self.url.path

        if (storetype == Datastore.SPARSE):
            self.writer = SparseWriter()
            return

        if (storetype == Datastore.GZIP1):
            self.writer = GZipWriter(1)
            return

        if (storetype == Datastore.GZIP6):
            self.writer = GZipWriter(6)

    def is_compressed(self):
        return self.writer.is_compressed()
        
    def saveData(self, node, srcpath):
        if (not self.local):
            raise ValueError("cannot save to remote datastores")

        if (not os.path.exists(srcpath)):
            raise ValueError("file does not exist")


        if not node.hash:
            node.hash = fileops.hash(srcpath)

        dstdir  = self.path + '/' + node.hash[:2]
        dstpath = self.getPath(node) 

        if os.path.exists(dstpath):
            return

        if (not os.path.exists(dstdir)):
            os.makedirs(dstdir)

        self.writer.write(srcpath, dstpath)

    def getURL(self, node):
        return urljoin(self.url.geturl(), self.getPath(node))

    def contents(self):
        retval = list()
        for dirname in os.listdir(self.path):
            for filename in os.listdir(self.path + '/' + dirname):
                filehash = dirname + filename[:38]
                filesize = filename[39:]
                retval.append((filehash , filesize))
        return retval

    def contains(self, node):
        return os.path.exists(self.getPath(node))

    def getPath(self, node):
        filehash = node.hash
        filesize = str(node.stats.st_size)
        return self.getPath2(filehash, filesize)

    def getPath2(self, filehash, filesize):
        return self.path + '/' + filehash[:2] + '/' + filehash[2:] + ':' + filesize

    def remove(self, filehash, filesize):
        os.remove(self.getPath2(filehash, filesize))

    def check(self, filehash, filesize):
        return filehash == fileops.hash(
            self.getPath2(filehash, filesize),
            self.is_compressed())

    local = property(lambda self: not ( self.path == None))

class Writer(object):
    pass

class SparseWriter(Writer):
    
    def write(self, srcpath, dstpath):
        srcfile = open(srcpath, 'rb')
        dstfile = open(dstpath,'wb')
        while True:
            buf = srcfile.read(4096)
            if not buf:
                break
            if buf == '\0'*len(buf):
                dstfile.seek(len(buf), os.SEEK_CUR)
            else:
                dstfile.write(buf)
        
        srcfile.close()
        dstfile.truncate()
        dstfile.close()

    def is_compressed(self):
        return False

class GZipWriter(Writer):
    
    def __init__(self, level):
        self.level = level

    def write(self, srcpath, dstpath):
        srcfile = open(srcpath, 'rb')
        dstfile = gzip.open(dstpath, 'wb', 
            compresslevel=self.level)
        #compression
        while True:
            buf = srcfile.read(16*1024)
            if not buf:
                break
            dstfile.write(buf)

        srcfile.close()
        dstfile.close()
    
    def is_compressed(self):
        return True
