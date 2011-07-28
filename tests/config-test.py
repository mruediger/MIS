import unittest
import io

import mfs.config


test_config = """
[datastore]
url = file://home/bag/projects/diplomarbeit/src/tmp/datastore
[repository]
url = file://home/bag/projects/diplomarbeit/src/tmp/repository
"""

class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = mfs.config.Config(io.BytesIO(test_config))


    def testGetDatastore(self):
        self.assertEquals("file://home/bag/projects/diplomarbeit/src/tmp/datastore", 
            self.config.datastore)
        self.config.datastore = '123'
        self.assertEquals('123',self.config.datastore)

    def testGetRepository(self):
        rp = self.config.repository
        self.assertEquals("file://home/bag/projects/diplomarbeit/src/tmp/repository",
            self.config.repository)
