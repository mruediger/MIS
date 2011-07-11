#!/usr/bin/python

import unittest
import mfs
import os
import stat

from StringIO import StringIO
from lxml import etree

from mfs.manifest import Directory,File,DeleteNode,Manifest

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
        childdict = dict()
        for child in manifest.root._children:
            childdict[child.name] = child
        self.assertTrue(stat.S_ISREG(childdict['testfile_a'].st_mode))
        self.assertTrue(stat.S_ISDIR(childdict['testdir'].st_mode))
        self.assertTrue(stat.S_ISCHR(childdict['mixer-testdev'].st_mode))
        self.assertEquals(os.stat('testdir/mixer-testdev').st_rdev, childdict['mixer-testdev'].st_rdev)

        self.assertFalse('.unionfs' in childdict)
        self.assertEquals(manifest.root._whiteouts[0].name, 'delnode:testfile_a')
        self.assertEquals(childdict['testdir']._whiteouts[0].name, 'delnode:another_file')
        

    def testDelNode(self):
        self.assertEquals(DeleteNode("test123"), DeleteNode("test123"))
    

    def testToXML(self):
        datastore = mfs.datastore.Datastore('datastore')
        manifest_orig = mfs.manifest.manifestFromPath('testdir', datastore)
        xml = etree.tostring(manifest_orig.toXML())
        manifest_new = mfs.manifest.manifestFromXML(StringIO(xml))
        self.assertEquals(manifest_orig, manifest_new)

        for child in manifest_new.root._children:
            if child.name == "testfile_a":
                child.name = "kartoffelbrei"
        self.assertNotEquals(manifest_orig, manifest_new)

    def testIterate(self):
        root = Directory("root")
        
        node = File("file_a")
        node.hash = "asdf1234"
        node.addTo(root)

        node = File("file_b")
        node.hash = "asdf5678"
        node.addTo(root)

        dirnode = Directory("dir")
        dirnode.addTo(root)

        node = File('subfile_a')
        node.hash = "fda1234"
        node.addTo(dirnode)

        node = File('subfile_b')
        node.hash = "fda1234"
        node.addTo(dirnode)

        manifest = Manifest(root)

        files = []

        for file in manifest:
            files.append(file)
        
        self.assertEquals(6,len(files))


if __name__ == '__main__':
    unittest.main()
