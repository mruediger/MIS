import unittest
import re

from mfs.autopatcher import Autopatcher

class AutopatcherTest(unittest.TestCase):
    
    def setUp(self):
        self.patcher = Autopatcher('tmp/autopatcher')

    def testParseConfig(self):
        self.assertEquals(2, len(self.patcher.listFiles()))

    def testScripts(self):
        print self.patcher.listFiles()
        output = self.patcher.getContent('/etc/hosts')
        self.assertFalse(output is None)
        self.assertTrue(output == 
"""HELLO WORLD
BLABLUBB
""")

    def testException(self):
        try:
            output = self.patcher.getContent('/etc/ssl/certs')
        except Exception as e:
            m = re.search("command not found", str(e))
            self.assertFalse(m is None)
