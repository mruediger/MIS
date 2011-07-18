#!/usr/bin/python

import unittest
import mfs
import os
import stat

from StringIO import StringIO
from lxml import etree

from mfs.manifest.nodes import Directory,File,Manifest

class TestManifest(unittest.TestCase):

    def setUp(self):
        pass

    def testSetStats(self):
        node = mfs.manifest.nodes.Directory('/tmp', os.stat('/tmp'))

        #check that all stats, except inode are set
        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            if (key == 'st_ino'): continue
            if (getattr(node,key) == None):
                print key
                self.assertFalse(True)

        manifest = mfs.manifest.serializer.fromPath('tmp/testdir')
        childdict = manifest.root.children_as_dict

        self.assertTrue(stat.S_ISDIR(childdict['testdir'].st_mode))
        self.assertTrue(stat.S_ISCHR(childdict['mixer-testdev'].st_mode))
        self.assertTrue(stat.S_ISREG(childdict['testdir'].children_as_dict['deeper_file'].st_mode))
        self.assertEquals(os.stat('tmp/testdir/mixer-testdev').st_rdev, childdict['mixer-testdev'].st_rdev)

        self.assertEquals('testfile_a', manifest.root._whiteouts[0].name)
        #self.assertEquals('another_file', childdict['testdir']._whiteouts[0].name)

    def testToXML(self):
        datastore = mfs.datastore.Datastore('tmp/datastore')
        manifest_orig = mfs.manifest.serializer.fromPath('tmp/testdir', datastore)
        xml = etree.tostring(manifest_orig.toXML(), pretty_print=True)
        manifest_new = mfs.manifest.serializer.fromXML(StringIO(xml))

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
