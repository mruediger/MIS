#!/usr/bin/python

import unittest

from copy import copy

from mfs.manifest.nodes import Directory, File, Manifest, DeleteNode, RMNode
from mfs.manifest.merge import merge


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
        target = self.orig + self.orig
        self.assertEquals(target.root, self.orig.root)
        self.assertEquals(target, self.orig)


        #merge doesnt modify sources
        target = self.orig + self.orig
        self.assertEquals(target, self.orig)
        target.root.stats.st_gid = 1234
        self.assertNotEquals(target, self.orig)

        #merge with empty
        newroot = Directory("orig")
        new = Manifest(newroot)
        target = self.orig + new
        self.assertEquals(target, self.orig)

    def testRecursive(self):
        """test merge with subfolders"""
        newroot = Directory("orig")
        testdir = Directory('testdir')

        testdir.addTo(newroot)
        File('new_file').addTo(testdir)
        deep_testdir = Directory('deep_testdir')
        deep_testdir.addTo(testdir)
        File('deep_testfile').addTo(deep_testdir)
        new = Manifest(newroot)
        target = self.orig + new
        self.assertTrue(
            newroot.children_as_dict['testdir'].children_as_dict['new_file'] ==
            target.root.children_as_dict['testdir'].children_as_dict['new_file'])
        
        self.assertFalse(
            newroot.children_as_dict['testdir'].children_as_dict['new_file'] is
            target.root.children_as_dict['testdir'].children_as_dict['new_file'])

        self.assertTrue(
            newroot.children_as_dict['testdir'].children_as_dict['deep_testdir'].children_as_dict['deep_testfile'] ==
            target.root.children_as_dict['testdir'].children_as_dict['deep_testdir'].children_as_dict['deep_testfile']
            )
        
        self.assertFalse(
            newroot.children_as_dict['testdir'].children_as_dict['new_file'] is
            target.root.children_as_dict['testdir'].children_as_dict['new_file'])


        newroot.children_as_dict['testdir'].children_as_dict['new_file'].stats.st_gid = 1234
        self.assertNotEquals(
            newroot.children_as_dict['testdir'].children_as_dict['new_file'], 
            target.root.children_as_dict['testdir'].children_as_dict['new_file'])

        self.assertTrue('another_dir' in target.root.children_as_dict['testdir'].children_as_dict)



    def testWhiteouts(self):
        """test merge of manifests containing whiteouts"""
        newroot = Directory('testdir')
        DeleteNode("testfile_a").addTo(newroot)
        DeleteNode("testfile_b").addTo(newroot)
        DeleteNode("testfile_a").addTo(self.orig.root)

        target = self.orig + Manifest(newroot)

        self.assertTrue("testfile_b" in target.root.children_as_dict)
        self.assertTrue("testfile_a" in target.root.children_as_dict)
        self.assertTrue(isinstance(target.root.children_as_dict["testfile_a"], DeleteNode))
        self.assertTrue(isinstance(target.root.children_as_dict["testfile_b"], DeleteNode))

    def testSubtractEmptyDir(self):
        newroot = Directory("orig")
        new = Manifest(newroot)
        target = self.orig - new

        self.assertFalse(target == self.orig)

        for node in target.root:
            self.assertTrue(isinstance(node, RMNode) or node == target.root)

    
    def testSubtractWithSelf(self):
        target = self.orig - self.orig
        new = Manifest(None)
        self.assertEquals(new, target)


    
    def testSubtractSingleFile(self):
        newroot = Directory("orig")
        testdir = Directory("testdir")
        another_dir = Directory("another_dir")
        deep_file = File("deep_file")

        another_dir.addTo(testdir)
        testdir.addTo(newroot)
        new = Manifest(newroot)

        self.assertFalse(self.orig.node_by_path('orig/testdir/another_dir/deep_file') is None)
        target = self.orig - new


        self.assertFalse(target.node_by_path('/testdir') is None)
        self.assertFalse(target.node_by_path('/testdir/another_dir/deep_file') is None)

        deep_file.addTo(another_dir)
        target = self.orig - new

        self.assertTrue(target.node_by_path('/testdir') is None)





    def testSubtractAllExceptOne(self):
        new = copy(self.orig)
        self.assertEquals(new, self.orig)
        
        testdir = new.root.children_as_dict['testdir']
        another_dir = testdir.children_as_dict['another_dir']
        another_dir._children = list()

        #check if only the file removed from new remains in target
        target = self.orig - new
        self.assertTrue(1, len(target.root._children))
        testdir = target.root.children_as_dict['testdir']
        self.assertTrue(1, len(testdir._children))
        another_dir = testdir.children_as_dict['another_dir']
        self.assertTrue(1, len(another_dir._children))
        self.assertTrue(isinstance(another_dir.children_as_dict['deep_file'], RMNode))

    def testHistory(self):
        new = copy(self.orig)
        target = self.orig + new
        self.assertTrue(target.is_child_off(self.orig))
        self.assertTrue(target.is_child_off(new))
        self.assertTrue(self.orig.is_parent_off(target))
        self.assertTrue(new.is_parent_off(target))


if __name__ == '__main__':
    unittest.main()
