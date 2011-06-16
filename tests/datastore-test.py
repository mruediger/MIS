#!/usr/bin/python

import unittest
import tempfile
import os
import shutil

from mfs.datastore import Datastore
from mfs.manifest  import File

class DatastoreTest(unittest.TestCase):

    def testCreation(self):
        try:
            datastore = Datastore()
        except ValueError as error:
            print error

    def testSaveDataWithMemStore(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")

        datastore = Datastore()
        datastore.saveData(node, tmpfile)
        self.assertEquals(file(tmpfile).read(), datastore.getData(node))

        os.remove(tmpfile)

    def testSaveDataWithDirStore(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir)
        datastore.saveData(node, tmpfile)
        self.assertEquals(file(tmpfile).read(), datastore.getData(node).read())
        

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)




unittest.main()

