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

        fobj = open(path, 'r')
        hl = hashlib.sha1()
        
        while True:
            data = fobj.read(1024 * 1024)
            if not data: break
            hl.update(data)

        node.hash = hl.hexdigest()
        self.store.saveData(node, fobj)

    def getPath(self, node):
        hashdir  = self.path + '/' + node.hash[:2]
        hashfile = hashdir + '/' + node.hash[2:]
        return (hashdir, hashfile)

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
            dest = file(destfile,'w')
            fobj.seek(0)
            buf = fobj.read(1024)
            while len(buf):
                dest.write(buf)
                buf = fobj.read(1024)

            dest.close()
            fobj.close()

    def getData(self, node):
        return open(self.path + '/' + node.hash[:2] + '/' + node.hash[2:])
