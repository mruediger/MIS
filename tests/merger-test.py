#!/usr/bin/python

import unittest

from mfs.manifest import Directory, File, Manifest
from mfs.manifest_merge import merge


class MergerTest(unittest.TestCase):
    def setUp(self):
        root = Directory("orig")
        root.children.append(File('testfile_a'))
        root.children.append(File('testfile_b'))

        testdir = Directory('testdir')
        root.children.append(testdir)
        another_dir = Directory('another_dir')
        testdir.children.append(another_dir)
        another_dir.children.append(File("deep_file"))
        root.children.append(Directory('second_testdir'))

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

        newroot.children.append(testdir)
        testdir.children.append(File('new_file'))
        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertEquals(
            newroot.children_as_dict()['testdir'].children_as_dict()['new_file'], 
            target.root.children_as_dict()['testdir'].children_as_dict()['new_file'])
        self.assertTrue('another_dir' in target.root.children_as_dict()['testdir'].children_as_dict())

    def testUnionfs(self):
        """test merge of unionfs folders"""  
        target = merge(self.orig, self.orig)
        self.assertFalse('testfile_a' not in target.root.children_as_dict())
        self.assertFalse('deep_file' not in target.root.children_as_dict()['testdir'].children_as_dict()['another_dir'].children_as_dict())


        newroot = Directory("orig")
        unionfsdir = Directory('.unionfs')
        newroot.children.append(unionfsdir)

        unionfsdir.children.append(File('testfile_a_HIDDEN~'))

        testdir = Directory('testdir')
        unionfsdir.children.append(testdir)

        another_dir = Directory('another_dir')
        testdir.children.append(another_dir)
        
        another_dir.children.append(File('deep_file_HIDDEN~'))

        
        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertTrue('.unionfs' not in target.root.children_as_dict())
        self.assertTrue('testfile_a' not in target.root.children_as_dict())
        self.assertTrue('deep_file' not in target.root.children_as_dict()['testdir'].children_as_dict()['another_dir'].children_as_dict())

    def testAUFS(self):
        """test merge of aufs folders"""

        #TODO test for deleted file hidden in subfolder

        target = merge(self.orig, self.orig)
        
        self.assertFalse('testfile_a' not in target.root.children_as_dict())
        self.assertFalse('deep_file' not in target.root.children_as_dict()['testdir'].children_as_dict()['another_dir'].children_as_dict())

        newroot = Directory("orig")
        newroot.children.append(File('.wh.testfile_a'))

        testdir = Directory('testdir')
        newroot.children.append(testdir)

        another_dir = Directory('another_dir')
        testdir.children.append(another_dir)

        another_dir.children.append(File('.wh.deep_file'))

        new = Manifest(newroot)
        target = merge(self.orig, new)

        self.assertTrue('testfile_a' not in target.root.children_as_dict())
        self.assertTrue('deep_file' not in target.root.children_as_dict()['testdir'].children_as_dict()['another_dir'].children_as_dict())


if __name__ == '__main__':
    unittest.main()
