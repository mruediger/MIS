#!/usr/bin/python

import unittest
import tempfile
import os
import shutil

from stat import *

from mfs.exporter import Exporter
from mfs.manifest import File, Directory, SymbolicLink
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

    def testExportFile(self):
        testfile = File("file")
        testfile.st_uid = 1000
        testfile.st_gid = 1000
        testfile.st_atime = 1234567
        testfile.st_mtime = 7654321
        testfile.st_nlink = 0
        testfile.st_mode  = 33188

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        datastore = Datastore()
        datastore.saveData(node, tmpfile)
        os.remove(tmpfile)

        testfile.hash = node.hash

        exporter = Exporter()
        exporter.export(testfile, self.tmpdir, datastore)
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'file'))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'file')[ST_ATIME])
        self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'file')[ST_MTIME])
        self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'file')[ST_MODE])


if __name__ == '__main__':
    unittest.main()
