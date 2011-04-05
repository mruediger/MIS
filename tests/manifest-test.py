#!/usr/bin/python

import unittest
import mfs

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
  
if __name__ == '__main__':
    unittest.main()
