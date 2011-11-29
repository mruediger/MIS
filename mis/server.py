import pickle
from mis.manifest.nodes import PatchNode,File

class MisServer(object):
    
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

    def getManifest(self, name, version=None, patchargs=[]):
        manifest = self.repository.getManifest(name, version)
	if self.autopatcher:
	        for filename in self.autopatcher.listFiles():
        	   node = manifest.node_by_path(filename)
	           if node is not None and isinstance(node, File):
        	        idx = node.parent._children.index(node)
	                content = self.autopatcher.getContent(
	                    filename, 
	                    self.datastore.getURL(node),
                	    patchargs)
        	        node.parent._children[idx] = PatchNode(node,content)
        return pickle.dumps(manifest)
