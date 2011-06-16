#!/usr/bin/python

import unittest
import tempfile
import os
import shutil

from stat import *

from mfs.exporter import Exporter
from mfs.manifest import File, Directory, Socket, SymbolicLink
from mfs.datastore import Datastore

class TestExport(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def testExportDirectory(self):
        directory = Directory("test")
        directory.st_uid   = 1000
        directory.st_gid   = 1000
        directory.st_atime = 1234567 
        directory.st_mtime = 12345678
        directory.st_mode  = 16866
        exporter = Exporter()
        exporter.export(directory, self.tmpdir, None)
        self.assertTrue(os.path.isdir(self.tmpdir + '/' + "test"))

        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + "test")[ST_ATIME])
        self.assertEquals(12345678, os.stat(self.tmpdir + '/' + "test")[ST_MTIME])

        self.assertEquals(16866, os.stat(self.tmpdir + '/' + "test")[ST_MODE])

if __name__ == '__main__':
    unittest.main()
