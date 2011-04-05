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

def run(mountpoint):
    init_logging()
    operations = mfs.fs.Operations(None)
    llfuse.init(operations, mountpoint, [])
    llfuse.main(single=True)
    llfuse.close()
    


if __name__ == '__main__':
    run(sys.argv[1])
