#!/usr/bin/python

import unittest
import mfs
import os
import stat

from lxml import etree

class TestManifest(unittest.TestCase):

    def setUp(self):
        pass

    def testSetStats(self):
        node = mfs.manifest.Directory('/tmp')
        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            setattr(node, key, None)

        node = mfs.manifest.Directory('/tmp', os.stat('/tmp'))

        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            if (key == 'st_ino') : continue
            if (getattr(node,key) == None):
                print key
                self.assertFalse(True)

        manifest = mfs.manifest.manifestFromPath('testdir')
        self.assertTrue(stat.S_ISREG(manifest.root.children['testfile'].st_mode))
        self.assertTrue(stat.S_ISDIR(manifest.root.children['testdir'].st_mode))
        self.assertTrue(stat.S_ISCHR(manifest.root.children['mixer-testdev'].st_mode))
        self.assertEquals(os.stat('testdir/mixer-testdev').st_rdev, manifest.root.children['mixer-testdev'].st_rdev)

    def testToXML(self):
        manifest = mfs.manifest.manifestFromPath('testdir')

if __name__ == '__main__':
    unittest.main()
