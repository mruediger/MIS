#!/usr/bin/python
    
import sys,os
import mfs

def export(argv):
    try:
        manifest_path  = argv[2]
        datastore_path = argv[3]
        destination_path = argv[4]
    except IndexError as e:
        print e
        return

    for dir in (destination_path, datastore_path):
        if not (os.path.exists(dir) and os.path.isdir(dir)):
            print ("ERROR: %s not a direfctory" % dir)
            return

    manifest = mfs.manifest.manifestFromPath(
        manifest_path,
        mfs.datastore.Datastore(datastore_path))

    for file in manifest:
        file.writeTo(destination)
    
    
def print_help(argv):
    pass


if __name__ == "__main__":
    {
        'export' : export
    }.get(sys.argv[1], print_help)(sys.argv)
