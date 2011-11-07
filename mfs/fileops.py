# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

"""MFS file operations
    
everything done with real file happenes here"""

#TODO copy might be better than read/write
#TODO shutil instead of own code?
#TODO copy and hash faster than separate invocations?
#TODO options for sparse file handling?

import os
import hashlib
import zlib
from urllib2 import urlopen

def hash(path):
    """reads the file and generates a hash"""
    hl = hashlib.sha1()
    with open(path, 'rb') as fsrc:
        while True:
             data = fsrc.read(16 * 4096)
             if not data: break
             hl.update(data)
        fsrc.close()
    return hl.hexdigest() 

def copy(src_url, dest_filename, sparsefile=False, compressed=False, blksize=(16*4096), filesize=None):
    fsrc = urlopen (src_url, 'rb')
    dcobj = zlib.decompressobj(16 + zlib.MAX_WBITS)
    with open(dest_filename, 'wb') as fdst:
        while True:
            buf = fsrc.read(blksize)
            if not buf:
                break
            if compressed:
                buf = dcobj.decompress(buf)
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
