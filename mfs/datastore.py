import os
import hashlib
import shutil

class Datastore(object):

    def __init__(self, path):
        if (not os.path.exists(path)):
            raise ValueError

        self.path = path

    def saveData(self, node, path):
        if (not os.path.exists(path)):
            raise ValueError

        fobj = open(path, 'r')
        hl = hashlib.sha1()


        while True:
            data = fobj.read(1024 * 1024)
            if not data: break
            hl.update(data)
        
        node.hash = hl.hexdigest()

        hashdir  = self.path + '/' + node.hash[:2]
        hashfile = hashdir + '/' + node.hash[2:]
    
        if (not os.path.exists(hashdir)):
            os.makedirs(hashdir)

        if (not os.path.exists(hashfile)):
            shutil.copyfile(path, hashfile)

    def getData(self, node, flags='r'):
        return open(self.path + '/' + node.hash[:2] + '/' + node.hash[2:])
