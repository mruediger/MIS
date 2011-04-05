import unittest
import hashlib

class TestFileStore(unittest.TestCase):
    
    def setUp(self):
        self.hl = hashlib.sha1()
        self.hl.update("TestString")

    def testHexDigestToPath(self):
        string = self.hl.hexdigest()
        path = [ string[:2], string[2:] ]
        self.assertEquals(path[0], string[:2])
        self.assertEquals(path[1], string[2:])

def hexdigestToPath(hexdigest):
    return [ hexdigest[2:], hexdigest[:2] ]


if __name__ == '__main__':
    unittest.main()

