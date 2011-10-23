#!/usr/bin/python 

import unittest
import copy
from mfs.manifest.nodes import *

class TestDiff(unittest.TestCase):

    def setUp(self):
        root = Directory('')
        self.manifest = Manifest(root)

    def testEquals(self):
        self.assertEquals(self.manifest, self.manifest)

        new_manifest = copy(self.manifest)
        self.assertEquals(self.manifest.root.stats, new_manifest.root.stats)
        self.assertEquals(self.manifest, new_manifest)

        new_manifest.root.name = "123"
        self.assertNotEquals(self.manifest, new_manifest)
        
    def testDiff(self):
        new_manifest = copy(self.manifest)
        
        #nodes
        new_manifest.root.name = "123"
        self.assertEquals('/ != 123 (name: /,123)', self.manifest.diff(new_manifest)[0])
        new_manifest.root.name  = "/"

        #stats
        new_manifest.root.stats.st_gid = "0"
        self.assertEquals('/ != / (st_gid: None,0)', self.manifest.diff(new_manifest)[0])

    def testDirectory(self):
        new_manifest = copy(self.manifest)
        File('testfile').addTo(new_manifest.root)
        self.assertEquals('testfile only in / (<)', self.manifest.diff(new_manifest)[0])

    def testRecDir(self):
        new_manifest = copy(self.manifest)
        file_a = File('testfile')
        file_a.addTo(new_manifest.root)
        file_b = File('testfile')
        file_b.addTo(self.manifest.root)
        self.assertEquals(self.manifest, new_manifest)

        self.manifest.root._children[0].stats.st_gid = "0"
        self.assertEquals('//testfile != //testfile (st_gid: 0,None)', self.manifest.diff(new_manifest)[0])

        self.manifest.root._children[0].name = "kartoffelbrei"
        self.assertEquals('kartoffelbrei only in / (>)', self.manifest.diff(new_manifest)[0])
        self.assertEquals('testfile only in / (<)', self.manifest.diff(new_manifest)[1])

if __name__ == "__main__":
    unittest.main()

