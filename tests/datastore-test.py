#!/usr/bin/python

import unittest
import tempfile
import os
import shutil
import urllib
import gzip 

from mfs.datastore import Datastore
from mfs.manifest.nodes  import File,Stats

class DatastoreTest(unittest.TestCase):

    def testGetURL(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))
        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir, Datastore.SPARSE)
        datastore.saveData(node, tmpfile)
        self.assertTrue( os.path.exists(datastore.getURL(node)[7:]) )

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)

    def testSaveDataSparse(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir, Datastore.SPARSE)
        datastore.saveData(node, tmpfile)
        self.assertEquals(file(tmpfile).read(), urllib.urlopen(datastore.getURL(node)).read())

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)
    
    def testSaveDataCompressed(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir, Datastore.GZIP6)
        datastore.saveData(node, tmpfile)
        self.assertEquals(file(tmpfile).read(), gzip.open(datastore.getPath(node),'r').read())

        os.remove(tmpfile)
        shutil.rmtree(tmpdir)

    def testCheckDatastoreSparse(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir, Datastore.SPARSE)
        datastore.saveData(node, tmpfile)   
        
        filehash , filesize = datastore.contents()[0]
        self.assertEquals(filehash, node.hash)
        self.assertEquals(filesize, str(node.stats.st_size))
        
        os.remove(tmpfile)
        shutil.rmtree(tmpdir)

    def testCheckDatastoreCompressed(self):
        (num, tmpfile) = tempfile.mkstemp()
        node = File(tmpfile)
        file(tmpfile, 'w').write("testcontent")
        node.stats = Stats(os.stat(tmpfile))

        tmpdir = tempfile.mkdtemp()
        datastore = Datastore(tmpdir, Datastore.GZIP6)
        datastore.saveData(node, tmpfile)   
        
        filehash , filesize = datastore.contents()[0]
        self.assertEquals(filehash, node.hash)
        self.assertEquals(filesize, str(node.stats.st_size))
        
        os.remove(tmpfile)
        shutil.rmtree(tmpdir)
