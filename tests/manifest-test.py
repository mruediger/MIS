#!/usr/bin/python

import unittest
import mfs
import os

from lxml import etree

class TestManifest(unittest.TestCase):

    def setUp(self):
        pass

    def testSetStats(self):
        node = mfs.manifest.Directory('/tmp')
        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            setattr(node, key, None)

        mfs.manifest.setStats(node, os.stat('/tmp'))

        for key in [ key for key in node.__slots__ if key.startswith("st_")]:
            if (key == 'st_ino') : continue
            if (getattr(node,key) == None):
                print key
                self.assertFalse(True)

    def testToXML(self):
        manifest = mfs.manifest.manifestFromPath('.')
        #xml = manifest.toXML()
        #string1 = etree.tostring(xml, pretty_print=True)
        #string2 = etree.tostring(mfs.manifest.manifestFromXML(xml).toXML(), pretty_print=True)

        s = raw_input("waiting")
        
        #keine ahnung wie ich das testen soll

if __name__ == '__main__':
    unittest.main()
