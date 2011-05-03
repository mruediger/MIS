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

    def testMerge(self):
        datastore = mfs.datastore.Datastore('datastore')
        manifest_orig = mfs.manifest.manifestFromPath('testdir', datastore)
        manifest_new = mfs.manifest.manifestFromPath('testdir', datastore)

        #basic
        manifest_merged = mfs.manifest.merge(manifest_orig, manifest_orig)
        self.assertEquals(manifest_orig, manifest_merged)

        #test rename
        tmp = manifest_new.root.children.pop('testfile_a')
        tmp.name = 'kartoffelbrei'
        manifest_new.root.children['kartoffelbrei'] = tmp
        self.assertNotEquals(manifest_orig, manifest_new)

        manifest_merged = mfs.manifest.merge(manifest_orig, manifest_new)
        self.assertTrue(manifest_merged.root.children.has_key('testfile_a'))
        self.assertTrue(manifest_merged.root.children.has_key('kartoffelbrei'))
        
        #test modify file
        manifest_new.root.children['kartoffelbrei'].hash = 123
        

        #test remove with unionfs
        manifest_new.root.children['.unionfs'] = mfs.manifest.Directory('.unionfs')
        manifest_new.root.children['.unionfs'].children['testfile_a_HIDDEN~'] = mfs.manifest.File('testfile_a_HIDDEN~')
        manifest_merged = mfs.manifest.merge(manifest_orig, manifest_new)
        self.assertFalse(manifest_merged.root.children.has_key('testfile_a'))
        self.assertTrue(manifest_merged.root.children.has_key('kartoffelbrei'))
        
        #test remove with unionfs recursive
        manifest_new.root.children['.unionfs'] = mfs.manifest.Directory('.unionfs')
        manifest_new.root.children['.unionfs'].children['testdir'] = mfs.manifest.Directory('testdir')
        manifest_new.root.children['.unionfs'].children['testdir'].children['another_file_HIDDEN~'] = mfs.manifest.File('another_file_HIDDEN~')
        manifest_merged = mfs.manifest.merge(manifest_orig, manifest_new)
        self.assertTrue(manifest_merged.root.children.has_key('testdir'))
        self.assertTrue(manifest_new.root.children['testdir'].children.has_key('another_file'))
        self.assertFalse(manifest_merged.root.children['testdir'].children.has_key('another_file'))

        #test remove with aufs
        #test remove with aufs recursive


if __name__ == '__main__':
    unittest.main()
