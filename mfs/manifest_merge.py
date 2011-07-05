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
            unionmerge(target.children_as_dict()[child.name], child)

def aufsmerge(target):
    todel = list()
    child_dict = target.children_as_dict()
    for child in target.children:
        if child.name.startswith('.wh.'):
            target.children.remove(child_dict[child.name.lstrip('.wh.')])
        elif isinstance(child, Directory):
            aufsmerge(child)

    for key in todel:
        target.children.remove(key)

def _merge(orig, new, target):
    assert isinstance(orig, Directory)
    assert isinstance(new, Directory)
    assert isinstance(target, Directory)

    tmp_children = dict()

    #copy original nodes
    for child in orig.children:
        tmp_children[child.name] = child.copy()

    #overwrite with changed nodes
    for child in new.children:
        tmp_children[child.name] = child.copy()

    target.children = tmp_children.values()

    #recursion through all nodes
    for child in target.children:
        if isinstance(child, Directory):
            try:
                _merge(
                    orig.children_as_dict().get(child.name, Directory("")), 
                    new.children_as_dict().get(child.name, Directory("")), 
                    child
                )
            except KeyError:
                continue


def children_to_dict(children):
    retval = dict()
    for child in children:
        retval[child.name] = child
    return retval

def merge(orig, new):
    target = orig.root.copy()
    _merge(orig.root, new.root, target)

    #check for unionfs
    for child in target.children:
        if (child.name == '.unionfs'):
            unionmerge(target, child)
            target.children.remove(child)

    #check for aufs
    if any( child.name.startswith('.wh') for child in target.children ):
        aufsmerge(target)

    return Manifest(target)
