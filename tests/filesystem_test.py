import unittest

from lxml import etree

from manifest import File
from create_datastore import toXML
from mount_datastore import fromXML

from filesystem import UnamedFS

class TestFileStore(unittest.TestCase):

    def setUp(self):
        self.root = File('/', is_directory=True)
        self.child1 = File(
            'test1', 
            is_directory=True)
        self.child2 = File(
            'test2', 
            is_directory=True)

        self.root.addChild(self.child1)
        self.child1.addChild(self.child2)


    def testToXML(self):
        self.child2.test = 123
        created_xml = etree.tostring(
                        toXML(self.root), 
                        pretty_print=True)

        xml = etree.fromstring(created_xml)
        tree = fromXML(xml)
        loaded_xml = etree.tostring(
                        toXML(tree), 
                        pretty_print=True)
        self.assertEquals(created_xml, loaded_xml)
        self.assertEquals(tree.getChild('/test1/test2').test, '123')


    def testListDir(self):
        fs = UnamedFS(self.root)
        self.assertEqual(fs.listdir('/test1/'), ['/test1/test2/'])
        self.assertEqual(fs.listdir("/", wildcard='x'), [])

if __name__ == '__main__':
    unittest.main()
