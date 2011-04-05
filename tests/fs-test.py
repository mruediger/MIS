#!/usr/bin/python

import unittest
import llfuse

from mfs import fs

class TestMFS(unittest.TestCase):
    """A TestCase for mfv.fs"""

    def setUp(self):
        self.fs = fs.Operations(None)

    def testUnimplemented(self):
        try:
            self.fs.flush(None)
        except llfuse.FUSEError as detail:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            

    def testImplemented(self):
        try:
            self.fs.getattr(123)
        except llfuse.FUSEError as detail:
            self.assertTrue(False)
        else:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
