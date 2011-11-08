import ConfigParser
from mfs.datastore import Datastore

class DatastoreConfig(object):
    pass

class Config(object):
    
    def __init__(self, fp):
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(fp)
    
    def getDatastore(self):
        retval = DatastoreConfig()
        retval.url = self.config.get('datastore','url')
        retval.type = eval("Datastore." + self.config.get('datastore','type'))
        return retval

    def setDatastore(self, url, type):
        self.config.set('datastore','url',url)
        self.config.set('datastore','type',type)

    def getRepository(self):
        return self.config.get('repository','url')

    def setRepository(self, url):
        self.config.set('repository','url',url)


    datastore  = property(getDatastore,setDatastore)
    repository = property(getRepository,setRepository)
