#!/usr/bin/python

import unittest

from mfs.manifest import Directory, File, Manifest, DeleteNode
from mfs.manifest_merge import merge


class MergerTest(unittest.TestCase):
    def setUp(self):
        root = Directory("orig")
        File('testfile_a').addTo(root)
        File('testfile_b').addTo(root)

        testdir = Directory('testdir')
        testdir.addTo(root)
        another_dir = Directory('another_dir')
        another_dir.addTo(testdir)
        File('deep_file').addTo(another_dir)
        Directory('second_testdir').addTo(root)

        self.orig = Manifest(root)

    def testBasics(self):
        """test merge on self"""

        #merge with self equals
        target = merge(self.orig, self.orig)
        self.assertEquals(target.root, self.orig.root)
        self.assertEquals(target, self.orig)

        #merge doesnt modify sources
        target = merge(self.orig, self.orig)
        self.assertEquals(target, self.orig)
        target.root.st_gid = 1234
        self.assertNotEquals(target, self.orig)

        #merge with empty
        newroot = Directory("orig")
        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertEquals(target, self.orig)

    def testRecursive(self):
        """test merge with subfolders"""
        newroot = Directory("orig")
        testdir = Directory('testdir')

        testdir.addTo(newroot)
        File('new_file').addTo(testdir)
        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertEquals(
            newroot.children_as_dict['testdir'].children_as_dict['new_file'], 
            target.root.children_as_dict['testdir'].children_as_dict['new_file'])
        self.assertTrue('another_dir' in target.root.children_as_dict['testdir'].children_as_dict)

    def testWhiteouts(self):
        """test merge of manifests containing whiteouts"""
        newroot = Directory('testdir')
        DeleteNode("testfile_a").addTo(newroot)
        DeleteNode("testfile_b").addTo(newroot)
        DeleteNode("testfile_a").addTo(self.orig.root)

        target = merge(self.orig, Manifest(newroot))

        self.assertEquals(2, len(target.root._whiteouts))
        self.assertEquals("testfile_a", target.root._whiteouts[0].name)
        self.assertEquals("testfile_b", target.root._whiteouts[1].name)

        self.assertTrue( any ( [ child.name == 'testfile_a' for child in target.root._children ] ) )
        
        target = merge(self.orig, Manifest(newroot), handle_whiteouts = True)

        self.assertFalse( any ( [ child.name == 'testfile_a' for child in target.root._children ] ) )

if __name__ == '__main__':
    unittest.main()
