# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

from mis.manifest.nodes import Directory, Manifest
from threading import Thread

import time


def merge_children(target, orig, new, handle_whiteouts):
    regnodes = set(orig._children + new._children)

    odict = orig.children_as_dict
    ndict = new.children_as_dict
    whiteouts = dict([ (wo.name, wo) for wo in (orig._whiteouts + new._whiteouts) ])
 
    for filename in [ child.name for child in regnodes]:

        #remove file and according whiteout during merge
        if (handle_whiteouts and filename in whiteouts):
            del whiteouts[filename]
            continue

        if (filename in ndict):
            newchild = ndict[filename].copy()
        else:
            newchild = odict[filename].copy()

        if isinstance(newchild, Directory):
            merge_children(
                newchild,
                odict.get(newchild.name, Directory("")),
                ndict.get(newchild.name, Directory("")),
                handle_whiteouts
            )
        target._children.append(newchild)

    target._whiteouts = whiteouts.values()

def merge(orig, new, handle_whiteouts=False):
    #TODO whiteout handling:
    # - whiteouts koennen optional dateien entfernen
    target = new.root.copy()
    merge_children(target, orig.root, new.root, handle_whiteouts)
    return Manifest(target)

