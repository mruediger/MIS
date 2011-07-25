#!/usr/bin/env python

import unittest
from mfs.repository import MemRepository

class VersioningTest(unittest.TestCase):
    
    def setUp(self):
        self.repository = MemRepository()
        self.repository.addXML("debian-1.xml")
        self.repository.addXML("debian-1.1.xml")

    def testListManifests(self):
        manifests = self.repository.getManifests()
        self.assertEquals(["debian"], manifests)

    def testGetVersions(self):
        versions = self.repository.getVersions("debian")
        self.assertEquals(['1','1.1'], versions)

    def testGetURL(self):
        url = self.repository.getURL("debian", "1.1")
        self.assertEquals('file://tmp/debian-1.1.xml', url)

if __name__ == "__main__":
    unittest.main()
