#!/usr/bin/python

import mfs

from lxml import etree

def run(sourcepath, datastore, output):
    manifest = mfs.manifest.manifestFromPath(
        sourcepath, 
        mfs.datastore.Datastore(datastore))

    xml = etree.tostring(manifest.toXML(), pretty_print=True)

    if (output is None):
        print xml
    else:
        pass

if __name__ == "__main__":
    import argparse, os, sys
    parser = argparse.ArgumentParser(
        description="Create a Manifest file and copy files to a Datastore if nessessary"
    )
    parser.add_argument('SOURCEPATH', type=str, help="path to import files from")
    parser.add_argument('DATASTORE', type=str, help="path to store data")
    parser.add_argument('-o','--output', type=str, help="store manifest to OUTPUT")
    args = parser.parse_args()

    #if not (os.path.exists(args.SOURCEPATH) and os.path.isdir(args.SOURCEPATH)):
     
    for var in ['SOURCEPATH','DATASTORE']:
        dir = vars(args)[var]
        if not (os.path.exists(dir) and os.path.isdir(dir)):
            print("ERROR: %s not a directory" % dir)
            sys.exit(1)
            

    run(
        sourcepath=args.SOURCEPATH,
        datastore=args.DATASTORE,
        output=args.output
    )
