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
            os.symlink(target + '/' + node.target, path)

        if isinstance(node, mfs.manifest.Device):
            os.makedev(
                os.major(node.st_rdev),
                os.minor(node.st_rdev)
                )

        if isinstance(node, mfs.manifest.FIFO):
            os.mkfifo(path)

        if isinstance(node, mfs.manifest.Directory):
            os.mkdir(path, mode=node.st_mode)

        if isinstance(node, mfs.manifest.File):
            if (node.st_nlink > 1):
                if (node.hash in self.linkcache):
                    os.link(self.linkcache[node.hash], path)
                    return
                else:
                    self.linkcache[node.hash] = path

            source = datastore.getData(node)
            dest = file(path, 'w')
            for data in source.read(1024):
                dest.write(data)
            dest.flush()

        
        os.chown(path, node.st_uid, node.st_gid)        #TODO security
        os.utime(path, (node.st_atime, node.st_mtime))
        os.chmod(path, node.st_mode)                    #TODO security

