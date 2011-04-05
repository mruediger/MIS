import fnmatch
import datetime

from fs.base import FS
from fs.errors import *
from fs.path import pathjoin,abspath

from StringIO import StringIO

class UnamedFS(FS):

    def __init__(self, syspath, manifest, datastore):
        self.manifest = manifest
        self.datastore = datastore
        self.syspath = syspath

    def open(self, path, mode='r', **kwargs):
        node = self.manifest.getPath(path)
        if (node is None):
            raise ResourceInvalidError(path,msg="Datastore Error")
        return self.datastore.getFile(node.hash)

    def isfile(self, path):
        return not self.manifest.getPath(path).is_directory()

    def isdir(self, path):
        return self.manifest.getPath(path).is_directory()


    def _listdir(self, path='./', wildcard=None, full=False, absolute=False, dirs_only=False, files_only=False):
        direntry = self.manifest.getPath(path)

        if (direntry is None):
            raise ResourceNotFoundError(path)

        if (not direntry.is_directory):
            raise ResourceInvalidError(path,msg="Not a directory")

        if (direntry.children == None):
            return []

        if (dirs_only and files_only):
            return []

        
        children = [ child.name for child in direntry.children.values() ]

        if (wildcard is not None):
            match = fnmatch.fnmatch
            children = [ c for c in children if match(c, wildcard) ]  

        if (dirs_only):
            children = [ c for c in children if c.is_directory ]
        if (files_only):
            children = [ c for c in children if not c.is_directory ]


        if full:
            children = [pathjoin(path, p) for p in children]
        elif absolute:
            children = [abspath(pathjoin(path, p)) for p in children]

        return [direntry, children]


    def listdir(self, path='./', wildcard=None, full=False, absolute=False, dirs_only=False, files_only=False):
        direntry, children = self._listdir (path,wildcard,full,absolute,dirs_only, files_only)
        return children


    def makedir(self, path, recursive=False, allow_recreate=False):
        raise UnsupportedError("makedir")

    def remove(self, path):
        raise UnsupportedError("remove")


    def removedir(self, path, recursive=False, force=False):
        raise UnsupportedError("removedir")

    def rename(self, src, dst):
        raise UnsupportedError("rename")

    def getinfo(self, path):
        node = self.manifest.getPath(path)
        if node is None:
            print "FOOBAR: " + path
            raise ResourceNotFoundError(path)

        return self.getinfoFromNode(node)

    def getinfoFromNode(self, node):
        stats = {}
        for k in dir(node.stats):
            if (k.startswith("st_")):
                stats[k] = getattr(node.stats, k)
        return stats

    def exists(self, path):
        return self.manifest.getPath(path) is not None
        

    #NON ESSENTIAL SPEEDUP METHODS

    def listdirinfo(path='./', wildcard=None, full=False, absolute=False, dirs_only=False, files_only=False):
        direntry, children = self._listdir (
                                path,
                                wildcard,
                                full,
                                absolute,
                                dirs_only, 
                                files_only)
        
        return [ (child, self.getinfoFromNode(direntry.children[child])) for child in children ]
 
#    def getsyspath(self, path, allow_none=False):
#        if not allow_none:
#            raise NoSysPathError(path=path)
#        return pathjoin(self.syspath, path)

    

