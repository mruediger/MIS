# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

"""MFS file operations
    
    fileoperations like read, write and hash are
    collected here"""


#TODO copy might be better than read/write
#TODO shutil instead of own code?
#TODO copy and hash faster than separate invocations?
#TODO options for sparse file handling?

def read(url):
    """reads a file and returns ... what excatly?"""
    pass

def hash(url):
    """reads the file and generates a hash"""
    pass

def write(url):
    """writes data to specified destination"""
    
