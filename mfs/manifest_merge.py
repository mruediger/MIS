from mfs.manifest import Directory, Manifest, DeleteNode
from threading import Thread

import time

def merge_children(orig, new):
    regnodes = set()
    delnodes = set()
    for child in orig.children + new.children:
        if isinstance(child, DeleteNode):
            delnodes.add(child)
        else:
            regnodes.add(child.name)

    odict = orig.children_as_dict
    ndict = new.children_as_dict
 

    retval = list()

    for filename in filenames:
        if (filename in ndict):
            newchild = ndict[filename].copy()
        else:
            newchild = odict[filename].copy()

        if isinstance(newchild, Directory):
            newchild.children = merge_children(
                odict.get(newchild.name, Directory("")),
                ndict.get(newchild.name, Directory(""))
            )
        retval.append(newchild)
        

    return retval + list(delnodes)
        

def merge(orig, new):
    target = new.root.copy()
    target.children = merge_children(orig.root, new.root)

    return Manifest(target)

