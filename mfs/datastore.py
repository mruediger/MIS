import os
import tempfile
from urlparse import urlparse, urlsplit, urljoin

import fileops

class Datastore(object):

    def __init__(self, url):
        if (url[-1] != '/'):
            url = url + '/'
        self.url = urlparse(url, 'file')
        self.path = self.url.path
        
    def saveData(self, node, path):
        if (not self.local):
            raise ValueError("cannot save to remote datastores")

        if (not os.path.exists(path)):
            raise ValueError("file does not exist")


        if not node.hash:
            node.hash = fileops.hash(path)

        destdir  = self.path + '/' + node.hash[:2]
        destfile = destdir   + '/' + node.hash[2:]

        if (not os.path.exists(destdir)):
            os.makedirs(destdir)

        dest = file(destfile,'wb')
        fobj = open(path, 'rb')

        #sparsefile handling from a shautil patch
        while True:
            buf = fobj.read(node.stats.st_blksize)
            if not buf:
                break
            if buf == '\0'*len(buf):
                dest.seek(len(buf), os.SEEK_CUR)
            else:
                dest.write(buf)

        dest.truncate()
        dest.close()
        fobj.close()

    def getURL(self, node):
        return urljoin(self.url.geturl(), self.toPath(node.hash))

    def contents(self):
        retval = list()
        for dirname in os.listdir(self.path):
            for filename in os.listdir(self.path + '/' + dirname):
                retval.append(dirname + filename)
        return retval

    def contains(self, node):
        return os.path.exists(self.toPath(node.hash))

    def toPath(self, filehash):
        return self.path + '/' + filehash[:2] + '/' + filehash[2:]

    def remove(self, filehash):
        os.remove(self.toPath(filehash))

    def check(self, filehash):
        return filehash == fileops.hash(
            self.toPath(filehash))

    local = property(lambda self: not ( self.path == None))
