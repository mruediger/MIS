import ConfigParser

class Config(object):
    
    def __init__(self, fp):
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(fp)
    
    def getDatastore(self):
        return self.config.get('datastore','url')

    def setDatastore(self, url):
        self.config.set('datastore','url',url)

    def getRepository(self):
        return self.config.get('repository','url')

    def setRepository(self, url):
        self.config.set('repository','url',url)


    datastore  = property(getDatastore,setDatastore)
    repository = property(getRepository,setRepository)
