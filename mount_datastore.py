#!/usr/bin/python

import llfuse
import sys
import logging

from lxml import etree

import mfs

def init_logging():
    formatter = logging.Formatter('%(message)s') 
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    log = logging.getLogger()
    log.setLevel(logging.INFO)    
    log.addHandler(handler)    

def run(mountpoint, manifest, datastore):
    init_logging()

    mf = open(manifest,'r')
    operations = mfs.fs.Operations(
        mfs.manifest.manifestFromXML(mf), 
        mfs.datastore.Datastore(datastore))

    mf.close()

    llfuse.init(operations, mountpoint, [])
    llfuse.main(single=True)
    llfuse.close()
    


if __name__ == '__main__':
    import argparse, os, sys
    parser = argparse.ArgumentParser(
        description="mounts a manifest"
    )
    parser.add_argument('MANIFEST', type=str, help="path to manifest file")
    parser.add_argument('DATASTORE', type=str, help="datastore to read from")
    parser.add_argument('MOUNTPOINT', type=str, help="the mountpoint")
    args = parser.parse_args()

    run(
        mountpoint = args.MOUNTPOINT,
        manifest = args.MANIFEST,
        datastore = args.DATASTORE
    )
