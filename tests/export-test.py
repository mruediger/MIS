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
        self.datastore = Datastore(tempfile.mkdtemp(), Datastore.SPARSE)
    
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        shutil.rmtree(self.datastore.path)
    
    def testExportDirectory(self):
        directory = Directory("test")
        directory.stats.st_uid   = 1000
        directory.stats.st_gid   = 1000
        directory.stats.st_atime = 1234567 
        directory.stats.st_mtime = 12345678
        directory.stats.st_mode  = 16866
        manifest = Manifest(directory)
        manifest.export(self.tmpdir, None)
        self.assertTrue(os.path.isdir(self.tmpdir + '/' + "test"))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + "test")[ST_ATIME])
        self.assertEquals(12345678, os.stat(self.tmpdir + '/' + "test")[ST_MTIME])
        self.assertEquals(16866, os.stat(self.tmpdir + '/' + "test")[ST_MODE])

    def testExportDirectoryContents(self):
        directory = Directory("testdir_with_content")
        directory.stats.st_uid   = 1000
        directory.stats.st_gid   = 1000
        directory.stats.st_atime = 1234567 
        directory.stats.st_mtime = 12345678
        directory.stats.st_mode  = 16866

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        node.stats = Stats(os.stat(tmpfile))
        file(tmpfile, 'w').write("testcontent")
        self.datastore.saveData(node, tmpfile)
        os.remove(tmpfile)
 
        for n in range(0,10):
            testfile = File("file" + str(n))
            testfile.stats = node.stats
            testfile.stats.st_uid = 1000
            testfile.stats.st_gid = 1000
            testfile.stats.st_atime = 1234567
            testfile.stats.st_mtime = 7654321
            testfile.stats.st_nlink = 1
            testfile.stats.st_mode  = 33188
            testfile.addTo(directory)
            testfile.hash = node.hash

        subdir = Directory('subdir')
        subdir.stats.st_uid = 1000
        subdir.stats.st_gid = 1000
        subdir.addTo(directory)
        subdir.stats.st_atime = 1234567
        subdir.stats.st_mtime = 7654321
        subdir.stats.st_mode  = 16866

        subfile = File('file')
        subfile.stats = node.stats
        subfile.hash = node.hash
        subfile.stats.st_uid = 1000
        subfile.stats.st_gid = 1000
        subfile.addTo(subdir)
        subfile.stats.st_atime = 1234567
        subfile.stats.st_mtime = 7654321
        subfile.stats.st_mode  = 33188
        subfile.stats.st_nlink = 1

        manifest = Manifest(directory)
        manifest.export(self.tmpdir, self.datastore)      

        for n in range(0,10):
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_content/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_content/file' + str(n))[ST_MODE])

        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_content/subdir/file'))

    def testExportFile(self):

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))
        self.datastore.saveData(node, tmpfile)
        os.remove(tmpfile)

        testfile = File("file")
        testfile.stats = node.stats
        testfile.stats.st_uid = 1000
        testfile.stats.st_gid = 1000
        testfile.stats.st_atime = 1234567
        testfile.stats.st_mtime = 7654321
        testfile.stats.st_nlink = 1
        testfile.stats.st_mode  = 33188
        testfile.hash = node.hash

        manifest = Manifest(testfile)
        manifest.export(self.tmpdir, self.datastore)
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'file'))
        self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'file')[ST_ATIME])
        self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'file')[ST_MTIME])
        self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'file')[ST_MODE])

        content = None
        with open(self.tmpdir + "/file") as src:
            content = src.read()

        src.close()
        self.assertEquals('testcontent', content)

    def testExportDevice(self):
        # this test is only possible with super user rights
        if (os.environ['USER'] != 'root'):
            return
        testdev = Device("mixer")
        testdev.stats.st_uid = 1000
        testdev.stats.st_gid = 1000
        testdev.stats.st_atime = 1234567
        testdev.stats.st_mtime = 7654321
        testdev.stats.st_nlink = 1
        testdev.rdev  = 64512L
        testdev.stats.st_mode  = 8612

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
        testlink.stats.st_uid = 1000
        testlink.stats.st_gid = 1000
        testlink.stats.st_atime = 1234567
        testlink.stats.st_mtime = 7654321
        testlink.stats.st_nlink = 1
        testlink.stats.st_mode  = 8612
        
        manifest = Manifest(testlink)
        manifest.export(self.tmpdir, None)

        self.assertTrue(os.path.exists(testlink.target))
        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testlink'))
        os.remove(tmpfile)

    def testFIFO(self):
        testfifo = FIFO("testfifo")
        testfifo.stats.st_uid = 1000
        testfifo.stats.st_gid = 1000
        testfifo.stats.st_atime = 1234567
        testfifo.stats.st_mtime = 7654321
        testfifo.stats.st_nlink = 1
        testfifo.stats.st_mode  = 8612
        
        manifest = Manifest(testfifo)
        manifest.export(self.tmpdir, None)

        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testfifo'))

    
    def testDirectoryWithWhiteouts(self):
        directory = Directory("testdir_with_whiteouts")
        directory.stats.st_uid   = 1000
        directory.stats.st_gid   = 1000
        directory.stats.st_atime = 1234567 
        directory.stats.st_mtime = 12345678
        directory.stats.st_mode  = 16866

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        node.stats = Stats(os.stat(tmpfile))
        file(tmpfile, 'w').write("testcontent")
        self.datastore.saveData(node, tmpfile)

        os.remove(tmpfile)
 
        for n in range(0,10):
            testfile = File("file" + str(n))
            testfile.stats = node.stats
            testfile.stats.st_uid = 1000
            testfile.stats.st_gid = 1000
            testfile.stats.st_atime = 1234567
            testfile.stats.st_mtime = 7654321
            testfile.stats.st_nlink = 1
            testfile.stats.st_mode  = 33188
            testfile.addTo(directory)
            testfile.hash = node.hash
            if (n == 2 or n == 4):
                WhiteoutNode("file" + str(n)).addTo(directory)

        manifest = Manifest(directory)
        manifest.export(self.tmpdir, self.datastore)      

        for n in range(0,10):
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])

        shutil.rmtree(self.tmpdir)
        self.tmpdir = tempfile.mkdtemp()

        manifest.export(self.tmpdir, self.datastore, whiteouts="unionfs")
        for n in range(0,10):
            if (n == 2 or n == 4):
                self.assertTrue(os.path.exists(self.tmpdir + '/' + '.unionfs/testdir_with_whiteouts/file' + str(n)))
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])

        shutil.rmtree(self.tmpdir)
        self.tmpdir = tempfile.mkdtemp()

        manifest.export(self.tmpdir, self.datastore, whiteouts="aufs")
        for n in range(0,10):
            if (n == 2 or n == 4):
                self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/.wh.file' + str(n)))
            self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n)))
            self.assertEquals(1234567, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_ATIME])
            self.assertEquals(7654321, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MTIME])
            self.assertEquals(33188, os.stat(self.tmpdir + '/' + 'testdir_with_whiteouts/file' + str(n))[ST_MODE])


    def testPatchNodes(self):
        directory = Directory("testdir_with_patchnodes")
        directory.stats.st_uid   = 1000
        directory.stats.st_gid   = 1000
        directory.stats.st_atime = 1234567 
        directory.stats.st_mtime = 12345678
        directory.stats.st_mode  = 16866

        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        node.stats = Stats(os.stat(tmpfile))
        file(tmpfile, 'w').write("testcontent")
        self.datastore.saveData(node, tmpfile)

        os.remove(tmpfile)

        testfile = File("file")
        testfile.stats = node.stats
        testfile.stats.st_uid = 1000
        testfile.stats.st_gid = 1000
        testfile.stats.st_atime = 1234567
        testfile.stats.st_mtime = 7654321
        testfile.stats.st_nlink = 1
        testfile.stats.st_mode  = 33188
        testfile.hash = node.hash

        patchnode = PatchNode(testfile, "foobar")
        patchnode.addTo(directory)

        manifest = Manifest(directory)
        manifest.export(self.tmpdir, self.datastore)

        self.assertTrue(os.path.exists(self.tmpdir + '/' + 'testdir_with_patchnodes'))

    
        content = None
        with open(self.tmpdir + "/file") as src:
            content = src.read()

        src.close()
        self.assertEquals('foobar', content)

if __name__ == '__main__':
    unittest.main()
