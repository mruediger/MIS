#!/usr/bin/python
    
import sys,os
import lxml

import mfs


def export_files(argv):
    """creates all files form the manifest in the provided directory"""
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
    manifest = mfs.manifest.serializer.fromXML(manifest_file)
    manifest.export(destination_path, datastore)

def import_files(argv):
    '''traveres through given path and creates a manifest'''
    try:
        path  = argv[0]
    except IndexError:
        print "usage: {0} import PATH".format(sys.argv[0])
        return

    manifest = mfs.manifest.serializer.fromPath(path)
    print lxml.etree.tostring(manifest.toXML(), pretty_print=True)

def datastore_cleanup(argv):
    """removes all files that are not in the manifest files provied as an argument"""
    pass

def datastore_store(argv):
    """stores all files specified in the manifest in the provided datastore location"""

    try:
        source = argv[0]
        xml_path  = argv[1]
        datastore_path = argv[2]
    except IndexError:
        print "usage {0} store SOURCE XML DATASTORE".format(sys.argv[0])
        return

    manifest = mfs.manifest.serializer.fromXML(xml_path)
    datastore = mfs.datastore.Datastore(datastore_path)

    for path, node in manifest.root.toPath(source):
        if isinstance (node, mfs.manifest.nodes.File):
            print "storing {0}".format(path)
            datastore.saveData(node, path)


if __name__ == "__main__":
    
    help_message = """usage: {0} <command> [<args>]""".format(sys.argv[0])
    help_message += """\navailable commands are:"""
    help_message += """\n   import : create a manifest from a directory"""
    help_message += """\n   export : store contents of a manifest to a directory"""
    help_message += """\n   store  : store files to datastore"""
    help_message += """\n   clean  : remove unneded files form datastore"""

    try:
        action = sys.argv[1]
    except IndexError:
        print help_message
        print sys.argv[0] + " too few arguments"
        sys.exit(1)
    
    if (action == "export"):
        export_files(sys.argv[2:])

    if (action == "import"):
        import_files(sys.argv[2:])

    if (action == "store"):
        datastore_store(sys.argv[2:])
