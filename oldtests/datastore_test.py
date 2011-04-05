import unittest

import datastore

class TestDatastore(unittest.TestCase):

    def setUp(self):
        self.datastore = datastore.Datastore("/dev/null")

    def testPathSplit(self):
        samplehash = "32e6b6abc0b3fa85851921910ece72b73cfa5cea"
        path =  self.datastore.getPath(samplehash)
        self.assertEquals(path, "/dev/null/32/e6b6abc0b3fa85851921910ece72b73cfa5cea")

if __name__ == '__main__':
    unittest.main()
