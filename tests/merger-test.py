#!/usr/bin/python

import unittest

from mfs.manifest import Directory, File, Manifest
from mfs.manifest_merge import merge


class MergerTest(unittest.TestCase):
    def setUp(self):
        root = Directory("orig")
        root.children['testfile_a'] = File('testfile_a')
        root.children['testfile_b'] = File('testfile_b')

        root.children['testdir'] = Directory('testdir')
        root.children['testdir'].children['another_dir'] = Directory('another_dir')
        root.children['testdir'].children['another_dir'].children['deep_file'] = File("deep_file")
        root.children['second_testdir'] = Directory('second_testdir')

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
        newroot = Directory("orig")
        newroot.children['testdir'] = Directory('testdir')
        newroot.children['testdir'].children['new_file'] = File('new_file')
        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertEquals(newroot.children['testdir'].children['new_file'], target.root.children['testdir'].children['new_file'])
        self.assertTrue('another_dir' in target.root.children['testdir'].children)

    def testUnionfs(self):
        """test merge of unionfs folders"""  
        target = merge(self.orig, self.orig)
        self.assertFalse('testfile_a' not in target.root.children)
        self.assertFalse('deep_file' not in target.root.children['testdir'].children['another_dir'].children)


        newroot = Directory("orig")
        newroot.children['.unionfs'] = Directory('.unionfs')
        newroot.children['.unionfs'].children['testfile_a_HIDDEN~'] = File('testfile_a_HIDDEN~')
        newroot.children['.unionfs'].children['testdir'] = Directory('testdir')
        newroot.children['.unionfs'].children['testdir'].children['another_dir'] = Directory('another_dir')
        newroot.children['.unionfs'].children['testdir'].children['another_dir'].children['deep_file_HIDDEN~'] = File('deep_file_HIDDEN~')

        new = Manifest(newroot)
        target = merge(self.orig, new)
        self.assertTrue('.unionfs' not in target.root.children)
        self.assertTrue('testfile_a' not in target.root.children)
        self.assertTrue('deep_file' not in target.root.children['testdir'].children['another_dir'].children)

    def testAUFS(self):
        """test merge of aufs folders"""
        target = merge(self.orig, self.orig)
        self.assertFalse('testfile_a' not in target.root.children)
        self.assertFalse('deep_file' not in target.root.children['testdir'].children['another_dir'].children)

        newroot = Directory("orig")
        newroot.children['.wh.testfile_a'] = File('.wh.testfile_a')
        newroot.children['testdir'] = Directory('testdir')
        newroot.children['testdir'] = Directory('testdir')
        newroot.children['testdir'].children['another_dir'] = Directory('another_dir')
        newroot.children['testdir'].children['another_dir'].children['.wh.deep_file'] = File('.wh.deep_file')

        new = Manifest(newroot)
        target = merge(self.orig, new)

        self.assertTrue('testfile_a' not in target.root.children)
        self.assertTrue('deep_file' not in target.root.children['testdir'].children['another_dir'].children)


if __name__ == '__main__':
    unittest.main()
