import urlparse

class Repository(object):
    
    def __init__(self):
        self.manifests = dict()

    def addXML(self, filename):
        index = filename.rfind('.')
        (name, _, version) = filename[:index].partition('-')

        if not name in self.manifests:
            self.manifests[name] = [ version ]
        else:
            self.manifests[name].append(version)

    def getManifests(self):
        return sorted(self.manifests.keys())

    def getVersions(self, name):
        return sorted(self.manifests[name])

class MemRepository(Repository):
    """Just for testing purposes"""

    def getURL(self, name, version):
        return urlparse.urljoin('file://tmp', name + '-' + version + '.xml')
