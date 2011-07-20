#!/usr/bin/python

import unittest
import pickle
import tempfile

import mfs

class PickleTest(unittest.TestCase):
    """Test the performance of pickle objects instead of serializing
    them as xml"""

    def testPickleCorrect(self):
        manifest = mfs.manifest.serializer.fromXML('debian.xml')
        pickle.dump(manifest, open('pickle','w'))

        new_manifest = pickle.load(open('pickle'))

        for line in manifest.diff(new_manifest):
            print line
        self.assertEquals(manifest, new_manifest)

    def testPickleSpeed(self):
        new_manifest = pickle.load(open('pickle'))

    def testXMLSpeed(self):
        manifest = mfs.manifest.serializer.fromXML('debian.xml')


if __name__ == "__main__":
    unittest.main()
