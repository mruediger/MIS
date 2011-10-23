import os
import hashlib
import tempfile
from urlparse import urlparse, urlsplit, urljoin

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

        fobj = open(path, 'rb')

        if not node.hash:
            #TODO why sha256?
            hl = hashlib.sha256()
        
            while True:
                data = fobj.read(1024 * 1024)
                if not data: break
                hl.update(data)

            node.hash = hl.hexdigest()

        destdir  = self.path + '/' + node.hash[:2]
        destfile = destdir   + '/' + node.hash[2:]

        if (not os.path.exists(destdir)):
            os.makedirs(destdir)

        dest = file(destfile,'wb')
        fobj.seek(0)

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
        with open(self.toPath(filehash), 'rb') as f:
            hl = hashlib.sha256()
            while True:
                data = f.read(16 * 4096)
                if not data: break
                hl.update(data)
            return hl.hexdigest() == filehash

    local = property(lambda self: not ( self.path == None))
