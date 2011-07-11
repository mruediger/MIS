from mfs.manifest import Directory, Manifest, DeleteNode
from threading import Thread

import time

def merge_children(target, orig, new):
    regnodes = set(orig._children + new._children)

    odict = orig.children_as_dict
    ndict = new.children_as_dict

 
    for filename in [ child.name for child in regnodes]:
        if (filename in ndict):
            newchild = ndict[filename].copy()
        else:
            newchild = odict[filename].copy()

        if isinstance(newchild, Directory):
            merge_children(
                newchild,
                odict.get(newchild.name, Directory("")),
                ndict.get(newchild.name, Directory(""))
            )
        target._children.append(newchild)
    
    target._whiteouts = list( set(orig._whiteouts) | set(new._whiteouts) ) 


def merge(orig, new):
    target = new.root.copy()
    merge_children(target, orig.root, new.root)

    return Manifest(target)

