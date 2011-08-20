import pickle

class MFSServer(object):
    
    def __init__(self, repository, autopatch):
        self.repository = repository
        self.autopatch = autopatch

    def _dispatch(self, method, params):
        try:
            value = getattr(self, method)(*params)
        except:
            import traceback
            traceback.print_exc()
            raise

        return value

    def listManifests(self):
        return self.repository.getManifests()

    def listVersions(self, name):
        return self.repository.getVersions(name)

    def getManifest(self, name, version=None):
        manifest = self.repository.getManifest(name, version)
        return pickle.dumps(manifest)
