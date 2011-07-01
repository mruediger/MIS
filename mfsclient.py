#!/usr/bin/python
    
import sys,os
import mfs

def export(argv):
    try:
        manifest_file  = argv[2]
        datastore_path = argv[3]
        destination_path = argv[4]
    except IndexError as e:
        print e
        return

    for dir in (destination_path, datastore_path):
        if not (os.path.exists(dir) and os.path.isdir(dir)):
            print ("ERROR: %s not a directory" % dir)
            return

    datastore = mfs.datastore.Datastore(datastore_path)

    manifest = mfs.manifest.manifestFromXML(manifest_file)

    from mfs.exporter import Exporter
    exporter = Exporter()

    for child in manifest.root.children.itervalues():
        exporter.export(child, destination_path, datastore)
    
    
def print_help(argv):
    pass


if __name__ == "__main__":
    {
        'export' : export
    }.get(sys.argv[1], print_help)(sys.argv)
