# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

import ConfigParser
from mis.datastore import Datastore

class DatastoreConfig(object):
    """Container class
    
    The DatastoreConfig class holds the path under which
    the datastores files are stored and the type, 
    (currently GZIP6, GZIP1 and SPARSE) which describes
    how files should be read and written. 
    
    """
    pass

class Config(object):
    """Easy access to configuration parameters"""
    
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
