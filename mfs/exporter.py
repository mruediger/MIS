import os.path
import mfs.manifest 

class Exporter(object):

    def __init__(self, target):
        self._target = os.path.abspath(target) + '/'
        self.linkcache = dict()
        self.directory = ""

    def getPath(self, node):
        return self._target + '/' + node.path

    def handleWhiteout(self, node):
        pass

class UnionFSExporter(Exporter):

    def handleWhiteout(self, node):
        parent = self._target + "/.unionfs/" + self.directory
        if not os.path.exists(parent):
            os.makedirs(parent)
        open(parent + '/' + node.name, 'a').close()


class AUFSExporter(Exporter):

    def handleWhiteout(self, node):
        open(self._target + '/' + self.directory + '/.wh.' + node.name, 'a').close()
