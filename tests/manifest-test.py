#!/usr/bin/python

import unittest
import mfs
import os

class TestManifest(unittest.TestCase):

    def setUp(self):
        pass

    def testDirectory(self):
        directory = mfs.manifest.Directory("testdir")
        self.assertEquals(directory.st_nlink, 2)
        self.assertEquals(directory.st_mode, 16877)

    def testFile(self):
        file = mfs.manifest.File("testfile")
        self.assertEquals(file.st_nlink, 1)
        self.assertEquals(file.st_mode, 33188)
        self.assertEquals(file.st_rdev, 0)
  
    def testSetStats(self):
        node = mfs.manifest.Directory('/tmp')
        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            setattr(node, key, None)

        mfs.manifest.setStats(node, os.stat('/tmp'))

        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            self.assertNotEquals(getattr(node,key), None)

    def testSearchFiles(self):
        root = mfs.manifest.searchFiles('.')
        print root

if __name__ == '__main__':
    unittest.main()
