import unittest
import pickle

from mis.server import MisServer
from mis.repository import MemRepository,FileRepository
from mis.manifest.nodes import Directory,File,Manifest
from mis.autopatcher import Autopatcher

class MisServerTest(unittest.TestCase):
    
    def setUp(self):
        root = Directory("")
        File("testfile-1").addTo(root)
        File("testfile-2").addTo(root)
        self.manifest = Manifest(root)
        self.patcher = Autopatcher('tmp/autopatcher')
        self.server = MisServer(MemRepository(), self.patcher, None)
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
        server = MisServer(FileRepository('tmp/repository'), self.patcher, None)
        manfest = pickle.loads(server.getManifest('testdir'))
