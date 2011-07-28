import unittest
import pickle

from mfs.server import MFSServer
from mfs.repository import MemRepository,FileRepository
from mfs.manifest.nodes import Directory,File,Manifest

class MFSServerTest(unittest.TestCase):
    
    def setUp(self):
        root = Directory("")
        File("testfile-1").addTo(root)
        File("testfile-2").addTo(root)
        self.manifest = Manifest(root)
        self.server = MFSServer(MemRepository())
        self.server.repository.addXML("debian-1.xml")
        self.server.repository.addXML("debian-1.1.xml",self.manifest)

    def testList(self):
        self.assertEquals(['debian'], self.server.listManifests())

    def testListVersions(self):
        self.assertEquals(['1','1.1'], self.server.listVersions('debian'))

    def testGetManifest(self):
        manifest = pickle.loads(self.server.getManifest('debian','1.1'))
        self.assertEquals(self.manifest, manifest)

    def testGetFileStore(self):
        server = MFSServer(FileRepository('tmp/repository'))
        manfest = pickle.loads(server.getManifest('testdir'))
