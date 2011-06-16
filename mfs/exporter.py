import os.path
import mfs.manifest 

class Exporter(object):

    def __init__(self):
        self.linkcache = dict()

    def export(self, node, target, datastore = None):
        #sanity checks:
        assert(os.path.isdir(target))

        path = target + '/' + node.name

        if isinstance(node, mfs.manifest.Socket):
            pass

        if isinstance(node, mfs.manifest.SymbolicLink):
            pass

        if isinstance(node, mfs.manifest.Device):
            pass

        if isinstance(node, mfs.manifest.FIFO):
            pass

        if isinstance(node, mfs.manifest.Directory):
            pass

        if isinstance(node, mfs.manifest.File):
            if (node.st_nlink > 1):
                if (node.hash in self.linkcache):
                    os.link(self.linkcache[node.hash], path)
                else:
                    self.linkcache[node.hash] = path
                    source = datastore.getData(node)
                    dest = file(target, 'w')
                    for data in source.read(1024):
                        dest.write(data)
                    dest.flush()

        
        os.chown(path, node.st_uid, node.st_gid)        #TODO security
        os.utime(path, (node.st_atime, node.st_mtime))
        os.chmod(path, node.st_mode)                    #TODO security

