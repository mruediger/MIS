#!/usr/bin/python

import unittest
from manifest import Manifest, Directory, File

class TestManifest(unittest.TestCase):
    
    def setUp(self):
        root = Directory('/')
        child1 = Directory('test1')
        child2 = File('test2')

        child1.addChild(child2)
        root.addChild(child1)
        self.manifest = Manifest(root)
        self.root = root
        self.child1 = child1
        self.child2 = child2

    def testGetPath(self):
        self.assertEquals(self.root, self.manifest.getPath('/'))
        self.assertEquals(self.child1, self.manifest.getPath('/test1'))
        self.assertEquals(self.child1, self.manifest.getPath('/test1/'))
        self.assertEquals(self.child2, self.manifest.getPath('/test1/test2'))

        self.assertEquals(None, self.manifest.getPath('/test2'))

                 
if __name__ == '__main__':
    unittest.main()
