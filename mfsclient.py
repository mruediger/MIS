#!/usr/bin/python
    
import sys,os
import mfs

def export(argv):
    try:
        manifest_file  = argv[0]
        datastore_path = argv[1]
        destination_path = argv[2]
    except IndexError as e:
        print "usage: {0} export MANIFEST DATASTORE DESTINATION".format(sys.argv[0])
        return

    for dir in (destination_path, datastore_path):
        if not (os.path.exists(dir) and os.path.isdir(dir)):
            print ("ERROR: %s not a directory" % dir)
            return

    datastore = mfs.datastore.Datastore(datastore_path)

    manifest = mfs.manifest.manifestFromXML(manifest_file)

    from mfs.exporter import Exporter
    exporter = Exporter()

    for child in manifest.root.children:
        exporter.export(child, destination_path, datastore)
    
def create(argv):
    try:
        source_path  = argv[0]
        datastore_path = argv[1]
    except IndexError:
        print "usage: {0} create PATH DATASTORE".format(sys.argv[0])
        return

    manifest = mfs.manifestFromPath(
        source_path,
        mfs.datastore.Datastore(datastore))

    print etree.tostring(manifest.toXML(), pretty_print=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="MFS Client"
    )
    parser.add_argument('ACTION', type=str, help="action to take", choices=["export", "merge", "mount"]
    )
    parser.add_argument('OPTION', type=str, nargs="*")
    args = parser.parse_args()
    
    if (args.ACTION == "export"):
        export(args.OPTION)
    else:
        parser.print_help()
