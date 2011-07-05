from mfs.manifest import Directory, Manifest
from threading import Thread

import time

def unionmerge(target, unionfsdir):
    for child in unionfsdir.children:
        if child.name.endswith('_HIDDEN~'):
            for checkdel in target.children:
                if checkdel.name == child.name.rstrip('_HIDDEN~'):
                    target.children.remove(checkdel)
        else:
            unionmerge(target.children_as_dict[child.name], child)

def merge_children(orig, new):
    filenames = set()
    for child in orig.children + new.children:
        filenames.add(child.name)

    odict = orig.children_as_dict
    ndict = new.children_as_dict
 

    retval = list()

    for filename in filenames:
                
        #filter AUFS files
        if ('.wh.' + filename in ndict):
            continue
        if ('.wh.' + filename in odict):
            continue

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
        

    return retval
        

def merge(orig, new):
    target = new.root.copy()
    target.children = merge_children(orig.root, new.root)

    #check for unionfs
    for child in target.children:
        if (child.name == '.unionfs'):
            unionmerge(target, child)
            target.children.remove(child)

    return Manifest(target)

