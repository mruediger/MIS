#!/usr/bin/python

import llfuse
import sys
import logging


import mfs

def init_logging():
    formatter = logging.Formatter('%(message)s') 
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    log = logging.getLogger()
    log.setLevel(logging.INFO)    
    log.addHandler(handler)    

def run(mountpoint, path):
    init_logging()
    root = mfs.manifest.searchFiles(path)
    manifest = mfs.manifest.Manifest(root)
    operations = mfs.fs.Operations(manifest)
    llfuse.init(operations, mountpoint, [])
    llfuse.main(single=True)
    llfuse.close()
    


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
