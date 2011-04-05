#!/usr/bin/python

import unittest
import yaml

from manifest import File
from manifest import Directory

class TestFileStore(unittest.TestCase):
    
    def setUp(self):
        self.root = Directory('/')
        self.child1 = Directory('test1')
        self.child2 = File('test2')

        self.root.addChild(self.child1)
        self.child1.addChild(self.child2)
                 
    def testFilestore(self):
        self.assertEqual(self.root.name, '/')
        self.assertEqual(self.root.path, '/')
        self.assertEqual(self.root.is_directory(), True)
        self.assertEqual(len(self.root.children),1)

    def testSerialize(self):
        dump = yaml.dump(self.root)
        tmp = yaml.load(dump)

        self.assertEqual(tmp.name, '/')
        self.assertEqual(tmp.is_directory(), True)
        self.assertEqual(tmp.children['test1'].name, 'test1')

    def testGetFile(self):
        self.assertEquals(self.root.getChild('/'), self.root)
        self.assertEquals(self.root.getChild('/test1'),self.child1)
        self.assertEquals(self.root.getChild('/test1/'),self.child1)
        self.assertEquals(self.root.getChild('/test1/test2'),self.child2)

if __name__ == '__main__':
    unittest.main()
