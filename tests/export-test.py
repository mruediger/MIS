#!/usr/bin/python

import unittest
import tempfile
import os
import shutil

from stat import *

from mfs.exporter import Exporter
from mfs.manifest.nodes import *
from mfs.datastore import Datastore

class TestExport(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        return
        shutil.rmtree(self.tmpdir)
    
    def testExportDirectory(self):
        directory = Directory("test")
        directory.st_uid   = 1000
        directory.st_gid   = 1000
        directory.st_atime = 1234567 
        directory.st_mtime = 12345678
        directory.st_mode  = 16866
        manifest = Manifest(directory)
        manifest.export(self.tmpdir, None)
        self.assertTrue(os.path.isdir(self.tmpdir + '/' + "test"))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + "test")[ST_ATIME])
        self.assertEquals(12345678, os.stat(self.tmpdir + '/' + "test")[ST_MTIME])
        self.assertEquals(16866, os.stat(self.tmpdir + '/' + "test")[ST_MODE])

    def testExportDirectoryContents(self):
        directory = Directory("testdir_with_content")
        directory.st_uid   = 1000
        directory.st_gid   = 1000
        directory.st_atime = 1234567 
        directory.st_mtime = 12345678
        directory.st_mode  = 16866

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        datastore = Datastore()
        datastore.saveData(node, tmpfile)
        os.remove(tmpfile)
 
        for n in range(0,10):
            testfile = File("file" + str(n))
            testfile.st_uid = 1000
            testfile.st_gid = 1000
            testfile.st_atime = 1234567
            testfile.st_mtime = 7654321
            testfile.st_nlink = 1
            testfile.st_mode  = 33188
            testfile.addTo(directory)
            testfile.hash = node.hash

        subdir = Directory('subdir')
        subdir.st_uid = 1000
        subdir.st_gid = 1000
        subdir.addTo(directory)
        subdir.st_atime = 1234567
        subdir.st_mtime = 7654321
        subdir.st_mode  = 16866

        subfile = File('file')
        subfile.st_uid = 1000
        subfile.st_gid = 1000
        subfile.addTo(subdir)
        subfile.st_atime = 1234567
        subfile.st_mtime = 7654321
        subfile.st_mode  = 33188
        subfile.st_nlink = 1
        subfile.hash = node.hash

        manifest = Manifest(directory)
        manifest.export(self.tmpdir, datastore)      

        for n in range(0,10):
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_content/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_MODE])

        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_content/subdir/file'))

    def testExportFile(self):
        testfile = File("file")
        testfile.st_uid = 1000
        testfile.st_gid = 1000
        testfile.st_atime = 1234567
        testfile.st_mtime = 7654321
        testfile.st_nlink = 1
        testfile.st_mode  = 33188

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        datastore = Datastore()
        datastore.saveData(node, tmpfile)
        os.remove(tmpfile)

        testfile.hash = node.hash

        manifest = Manifest(testfile)
        manifest.export(self.tmpdir, datastore)
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'file'))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'file')[ST_ATIME])
        self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'file')[ST_MTIME])
        self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'file')[ST_MODE])

    def testExportDevice(self):
        # this test is only possible with super user rights
        if (os.environ['USER'] != 'root'):
            return
        testdev = Device("mixer")
        testdev.st_uid = 1000
        testdev.st_gid = 1000
        testdev.st_atime = 1234567
        testdev.st_mtime = 7654321
        testdev.st_nlink = 1
        testdev.st_rdev  = 64512L
        testdev.st_mode  = 8612

        manifest = Manifest(testdev)
        manifest.export(self.tmpdir, None)
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'mixer'))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'mixer')[ST_ATIME])
        self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'mixer')[ST_MTIME])
        self.assertEquals(8612, os.stat(self.tmpdir + '/' + 'mixer')[ST_MODE])

    def testSymbolicLink(self):
        (num, tmpfile) = tempfile.mkstemp()

        testlink = SymbolicLink("testlink")
        testlink.target = tmpfile
        testlink.st_uid = 1000
        testlink.st_gid = 1000
        testlink.st_atime = 1234567
        testlink.st_mtime = 7654321
        testlink.st_nlink = 1
        testlink.st_mode  = 8612
        
        manifest = Manifest(testlink)
        manifest.export(self.tmpdir, None)

        self.assertTrue(os.path.exists(testlink.target))
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testlink'))
        os.remove(tmpfile)

    def testFIFO(self):
        testfifo = FIFO("testfifo")
        testfifo.st_uid = 1000
        testfifo.st_gid = 1000
        testfifo.st_atime = 1234567
        testfifo.st_mtime = 7654321
        testfifo.st_nlink = 1
        testfifo.st_mode  = 8612
        
        manifest = Manifest(testfifo)
        manifest.export(self.tmpdir, None)

        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testfifo'))

    
    def testDirectoryWithWhiteouts(self):
        directory = Directory("testdir_with_whiteouts")
        directory.st_uid   = 1000
        directory.st_gid   = 1000
        directory.st_atime = 1234567 
        directory.st_mtime = 12345678
        directory.st_mode  = 16866

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        datastore = Datastore()
        datastore.saveData(node, tmpfile)

        print tmpfile

        #os.remove(tmpfile)
 
        for n in range(0,10):
            testfile = File("file" + str(n))
            testfile.st_uid = 1000
            testfile.st_gid = 1000
            testfile.st_atime = 1234567
            testfile.st_mtime = 7654321
            testfile.st_nlink = 1
            testfile.st_mode  = 33188
            testfile.addTo(directory)
            testfile.hash = node.hash
            if (n == 2 or n == 4):
                DeleteNode("file" + str(n)).addTo(directory)

        manifest = Manifest(directory)
        manifest.export(self.tmpdir, datastore)      

        for n in range(0,10):
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])

        shutil.rmtree(self.tmpdir)
        self.tmpdir = tempfile.mkdtemp()

        manifest.export(self.tmpdir, datastore, whiteouts="unionfs")
        for n in range(0,10):
            if (n == 2 or n == 4):
                self.assertTrue(os.path.exists(self.tmpdir + '/' + '.unionfs/testdir_with_whiteouts/file' + str(n)))
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])

        shutil.rmtree(self.tmpdir)
        self.tmpdir = tempfile.mkdtemp()

        manifest.export(self.tmpdir, datastore, whiteouts="aufs")
        for n in range(0,10):
            if (n == 2 or n == 4):
                self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/.wh.file' + str(n)))
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])

if __name__ == '__main__':
    unittest.main()
