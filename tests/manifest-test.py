#!/usr/bin/python

import unittest
import mfs
import os
import stat

from StringIO import StringIO
from lxml import etree

class TestManifest(unittest.TestCase):

    def setUp(self):
        pass

    def testSetStats(self):
        node = mfs.manifest.Directory('/tmp', os.stat('/tmp'))

        #check that all stats, except inode are set
        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            if (key == 'st_ino'): continue
            if (getattr(node,key) == None):
                print key
                self.assertFalse(True)

        manifest = mfs.manifest.manifestFromPath('testdir')
        self.assertTrue(stat.S_ISREG(manifest.root.children['testfile_a'].st_mode))
        self.assertTrue(stat.S_ISDIR(manifest.root.children['testdir'].st_mode))
        self.assertTrue(stat.S_ISCHR(manifest.root.children['mixer-testdev'].st_mode))
        self.assertEquals(os.stat('testdir/mixer-testdev').st_rdev, manifest.root.children['mixer-testdev'].st_rdev)

    def testToXML(self):
        datastore = mfs.datastore.Datastore('datastore')
        manifest_orig = mfs.manifest.manifestFromPath('testdir', datastore)
        xml = etree.tostring(manifest_orig.toXML())
        manifest_new = mfs.manifest.manifestFromXML(StringIO(xml))
        self.assertEquals(manifest_orig, manifest_new)

        manifest_new.root.children['testfile_a'].name = "kartoffelbrei"
        self.assertNotEquals(manifest_orig, manifest_new)


if __name__ == '__main__':
    unittest.main()
