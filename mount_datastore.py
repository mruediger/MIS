#!/usr/bin/python

import sys

from fs.expose import fuse
from lxml import etree

from manifest import File,Directory,Manifest
from datastore import Datastore
from filesystem import UnamedFS

def fromXML(xml):
    if (xml.attrib['type'] == "file"):
        node = File()
    else:
        node = Directory()

    for child in xml:
        if (child.tag == 'file'):
            node.addChild(fromXML(child))
        else:
            if child.tag.startswith('st_'):
                t = child.attrib['type']
                if (t == 'bool'):
                    node.stats[child.tag] = bool(child.text)
                if (t == 'float'):
                    node.stats[child.tag] = float(child.text)
                if (t == 'int'):
                    node.stats[child.tag] = int(child.text)
                if (t == 'long'):
                    print child.tag
                    node.stats[child.tag] = long(child.text)
                if (t == 'str'):
                    node.stats[child.tag] = str(child.text)
            elif not child.tag.startswith('_'):
                    setattr(node,child.tag, child.text)

    return node
            

def run():
    if len(sys.argv) != 4:
        print sys.argv[0] + " manifest datastore target_dir"
        sys.exit(1)

    xml_file = open(sys.argv[1],'r')
    xml = etree.parse(xml_file)
    manifest = Manifest(fromXML(xml.getroot()))
    datastore = Datastore(sys.argv[2]) 
    fs = UnamedFS(
        sys.argv[3],    
        manifest,
        datastore)

    fuse.mount(fs,sys.argv[3],foreground=True)


if __name__ == '__main__':
    import trace
    tracer = trace.Trace( 
            ignoredirs = [],
            trace = 0) 
    tracer.run("run()")
    r = tracer.results() 
    r.write_results(show_missing=True, coverdir="ergebnis")

