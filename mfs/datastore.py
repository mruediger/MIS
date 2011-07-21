import os
import hashlib
import urlparse
import tempfile

class Datastore(object):

    def __init__(self, path):
        if (not os.path.exists(path)):
            raise ValueError("path does not exist")
        self.path = path
        self.url = "file://" + os.path.abspath(path) + '/'

    def saveData(self, node, path):
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
        return urlparse.urljoin(self.url, node.hash[:2] + '/' + node.hash[2:])

    def getData(self, node):
        return open(self.path + '/' + node.hash[:2] + '/' + node.hash[2:])

    def contents(self):
        retval = list()
        for dirname in os.listdir(self.path):
            for filename in os.listdir(self.path + '/' + dirname):
                retval.append(dirname + filename)
        return retval

    def contains(self, node):
        return os.path.exists(self.path + '/' + node.hash[:2] + '/' + node.hash[2:])

    def check(self, filehash):
        with open(self.path + '/' + filehash[:2] + '/' + filehash[2:], 'rb') as f:
            hl = hashlib.sha256()
            while True:
                data = f.read(16 * 4096)
                if not data: break
                hl.update(data)
            return hl.hexdigest() == filehash
