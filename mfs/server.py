import pickle
from mfs.manifest.nodes import PatchNode,File

class MFSServer(object):
    
    def __init__(self, repository, autopatcher, datastore):
        self.repository = repository
        self.datastore = datastore
        self.autopatcher = autopatcher

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
        if self.autopatcher and self.datastore:
            for filename in self.autopatcher.listFiles():
               node = manifest.node_by_path(filename)
               if node is not None and isinstance(node, File):
                    idx = node.parent._children.index(node)
                    del node.parent._children[idx]
                    content = self.autopatcher.getContent(filename, self.datastore.getURL(node))
                    node.parent._children.append(PatchNode(node,content))
        return pickle.dumps(manifest)
