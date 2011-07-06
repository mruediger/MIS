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
            try:
                os.symlink(node.target, path)
            except OSError:
                print "ERROR: " + path
            return

        if isinstance(node, mfs.manifest.Device):
            os.mknod(path, node.st_mode, os.makedev(
                os.major(node.st_rdev),
                os.minor(node.st_rdev)
                ))

        if isinstance(node, mfs.manifest.FIFO):
            os.mkfifo(path)

        if isinstance(node, mfs.manifest.Directory):
            try:
                os.mkdir(path)
            except OSError:
                pass

            for child in node.children:
                self.export(child, path, datastore)

        if isinstance(node, mfs.manifest.File):
            if (node.st_nlink > 1):
                if (node.orig_inode in self.linkcache):
                    os.link(self.linkcache[node.orig_inode], path)
                    return
                else:
                    self.linkcache[node.orig_inode] = path

            source = datastore.getData(node)
            dest = file(path, 'w')
            
            buf = source.read(1024)
            while len(buf):
                buf = source.read(1024)
                dest.write(buf)

            source.close()
            dest.close()

        
        os.chown(path, node.st_uid, node.st_gid)        #TODO security
        os.utime(path, (node.st_atime, node.st_mtime))
        #os.chmod(path, node.st_mode)                    #TODO security

