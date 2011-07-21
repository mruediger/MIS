# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

"""MFS file operations
    
everything done with real file happenes here"""

#TODO copy might be better than read/write
#TODO shutil instead of own code?
#TODO copy and hash faster than separate invocations?
#TODO options for sparse file handling?

import os
from urllib2 import urlopen

def hash(url):
    """reads the file and generates a hash"""
    pass

def copy(src_url, dest_filename, sparsefile=False, blksize=(16*4096), filesize=None):
    fsrc = urlopen (src_url, 'rb')
    with open(dest_filename, 'wb') as fdst:
        while True:
            buf = fsrc.read(blksize)
            if not buf:
                break
            if sparsefile and buf == '\0'*len(buf):
                fdst.seek(len(buf), os.SEEK_CUR)
            else:
                fdst.write(buf)

        if filesize:
            fdst.seek(0)
            fdst.truncate(filesize)
        else:
            fdst.truncate()

        fdst.close()
        fsrc.close()
