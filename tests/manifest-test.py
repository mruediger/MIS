#!/usr/bin/python

import unittest
import mfs
import os
import stat

from StringIO import StringIO
from lxml import etree

from mfs.manifest import Directory,File,Manifest

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

    def testIterate(self):
        root = Directory("root")
        root.children['file_a'] = File("file_a")
        root.children['file_a'].hash = "asdf1234"
        root.children['file_b'] = File("file_b")
        root.children['file_b'].hash = "asdf5678"
        root.children['dir'] = Directory("dir")
        root.children['dir'].children['subfile_a'] = File('subfile_a')
        root.children['dir'].children['subfile_a'].hash = "fda1234"

        root.children['dir'].children['subfile_b'] = File('subfile_b')
        root.children['dir'].children['subfile_b'].hash = "fda1234"
        manifest = Manifest(root)

        files = []

        for file in manifest:
            files.append(file)
        
        self.assertEquals(6,len(files))


if __name__ == '__main__':
    unittest.main()
