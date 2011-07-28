import pickle

class MFSServer(object):
    
    def __init__(self, repository):
        self.repository = repository

    def _dispatch(self, method, params):
        return getattr(self, method)(*params)

    def listManifests(self):
        return self.repository.getManifests()

    def listVersions(self, name):
        return self.repository.getVersions(name)

    def getManifest(self, name, version=None):
        manifest = self.repository.getManifest(name, version)
        return pickle.dumps(manifest)
