class Datastore:
    
    def __init__(self,path):
        self.path = path

    def getFile(self,filehash,mode='r'):
        return open(self.getPath(filehash), mode)

    def getPath(self,filehash):
        return self.getDirName(filehash) + "/" + self.getFileName(filehash)
    
    def getDirName(self,filehash):
        return self.path + "/" + filehash[:2]

    def getFileName(self,filehash):
        return filehash[2:]

