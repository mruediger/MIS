import os
import hashlib

class Datastore(object):

    def __init__(self, path=None):
        if path is None:
            self.store = MemStore()
        else:
            if (not os.path.exists(path)):
                raise ValueError("path does not exist")
            self.store = DirStore(path)

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
        self.store.saveData(node, fobj)

    def getPath(self, node):
        return self.store.path + '/' + node.hash[:2] + '/' + node.hash[2:]

    def getData(self, node):
        return self.store.getData(node)

class MemStore(object):

    def __init__(self):
        self.data = dict()

    def saveData(self, node, fobj):
        fobj.seek(0)
        self.data[node.hash] = MemStoreContainer(fobj.read())
        fobj.close()

    def getData(self, node):
        return self.data[node.hash]

class MemStoreContainer(object):
    
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, count=0):
        if (count == 0):
            return self.data
        else:
            pos = self.pos
            self.pos = pos+count
            return self.data[pos:pos+count]

    def close(self):
        pass

class DirStore(object):
    def __init__(self, path):
        self.path = path

    def saveData(self, node, fobj):
        destdir  = self.path + '/' + node.hash[:2]
        destfile = destdir   + '/' + node.hash[2:]

        if (not os.path.exists(destdir)):
            os.makedirs(destdir)
        if (not os.path.exists(destfile)):
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

    def getData(self, node):
        return open(self.path + '/' + node.hash[:2] + '/' + node.hash[2:])
