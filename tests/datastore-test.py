#!/usr/bin/python

import unittest
import tempfile
import os
import shutil
import urllib

from mfs.datastore import Datastore
from mfs.manifest.nodes  import File,Stats

class DatastoreTest(unittest.TestCase):

    def testGetURL(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))
        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir)
        datastore.saveData(node, tmpfile)
        self.assertTrue( os.path.exists(datastore.getURL(node)[7:]) )

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)

    def testSaveData(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir)
        datastore.saveData(node, tmpfile)
        self.assertEquals(file(tmpfile).read(), urllib.urlopen(datastore.getURL(node)).read())
        

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)
