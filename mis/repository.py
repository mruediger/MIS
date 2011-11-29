# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

import urlparse
import os

import mis

"""A repository class for manifest files, either backed by memory or 
a directory containing xml files"""

class Repository(object):
    
    def __init__(self):
        self.manifests = dict()

    def addXML(self, filename):
        index = filename.rfind('.')
        (name, _, version) = filename[:index].partition('-')

	print name
	print version

        if not name in self.manifests:
            self.manifests[name] = [ version ]
        else:
            self.manifests[name].append(version)

    def getManifests(self):
        return sorted(self.manifests.keys())

    def getVersions(self, name):
        return sorted(self.manifests[name])

    def getManifest(self, name, version):
        pass

class MemRepository(Repository):
    """Just for testing purposes"""

    def __init__(self):
        Repository.__init__(self)
        self.data = dict()

    def addXML(self, filename, manifest=None):
        Repository.addXML(self, filename)
        
        index = filename.rfind('.')
        if (manifest):
            self.data[filename[:index]] = manifest

    def getManifest(self, name, version=""):
        filename = name + "-" + version
        return self.data[filename] 
        
class FileRepository(Repository):
    
    def __init__(self, directory):
        Repository.__init__(self)
        self.directory = os.path.abspath(directory)
        for filename in os.listdir(directory):
            Repository.addXML(self,filename)

    def getManifest(self, name, version=None):
        if version:
            filename = name + '-' + version + '.xml'
        else:
            versions = sorted(self.manifests[name])
            if ( versions != [''] ):
                filename = name + '-' + versions[-1] + '.xml'
            else:
                filename = name + '.xml'

        manifest = mis.manifest.serializer.fromXML(self.directory + '/' + filename)
        return manifest
