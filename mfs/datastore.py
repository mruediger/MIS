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
        destfile = self.toPath(node) 

        if (not os.path.exists(destdir)):
            os.makedirs(destdir)

        if os.path.exists(destfile):
            return

        dest = file(destfile,'wb')
        fobj = open(path, 'rb')

        #sparsefile handling from a shautil patch
        while True:
            buf = fobj.read(512)
            if not buf:
                break
            if buf == '\0'*len(buf):
                dest.seek(len(buf), os.SEEK_CUR)
            else:
                dest.write(buf)

        fobj.close()
        dest.truncate()
        dest.close()

    def getURL(self, node):
        return urljoin(self.url.geturl(), self.toPath(node))

    def contents(self):
        retval = list()
        for dirname in os.listdir(self.path):
            for filename in os.listdir(self.path + '/' + dirname):
                filehash = dirname + filename[:38]
                filesize = filename[39:]
                retval.append((filehash , filesize))
        return retval

    def contains(self, node):
        return os.path.exists(self.toPath(node.hash))

    def toPath(self, node):
        filehash = node.hash
        filesize = str(node.stats.st_size)
        return self.toPath2(filehash, filesize)

    def toPath2(self, filehash, filesize):
        return self.path + '/' + filehash[:2] + '/' + filehash[2:] + ':' + filesize

    def remove(self, filehash, filesize):
        os.remove(self.toPath2(filehash, filesize))

    def check(self, filehash, filesize):
        return filehash == fileops.hash(
            self.toPath(filehash))

    local = property(lambda self: not ( self.path == None))
