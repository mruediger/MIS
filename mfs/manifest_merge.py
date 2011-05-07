from mfs.manifest import Directory, Manifest
from threading import Thread

import time

def unionmerge(target, unionfsdir):
    for key in unionfsdir.children.iterkeys():
        if key.endswith('_HIDDEN~'):
            del target.children[key.rstrip('_HIDDEN~')]
        else:
            unionmerge(target.children[key], unionfsdir.children[key])

def aufsmerge(target):
    todel = list()
    for key in list(target.children.iterkeys()):
        if key.startswith('.wh.'):
            todel.append(key.lstrip('.wh.'))
        elif isinstance(target.children[key], Directory):
            aufsmerge(target.children[key])

    for key in todel:
        del target.children[key]

def _merge(orig, new, target):
    assert isinstance(orig, Directory)
    assert isinstance(new, Directory)
    assert isinstance(target, Directory)

    #copy original nodes
    for name, child in orig.children.iteritems():
        target.children[name] = child.copy()

    #overwrite with changed nodes
    for name, child in new.children.iteritems():
        target.children[name] = child.copy()

    #recursion through all nodes

    for name in target.children.iterkeys():
        if isinstance(target.children[name], Directory):
            try:
                _merge(
                    orig.children.get(name, Directory("")), 
                    new.children.get(name, Directory("")), 
                    target.children.get(name)
                )
            except KeyError:
                continue

def merge(orig, new):
    target = orig.root.copy()
    _merge(orig.root, new.root, target)

    #check for unionfs
    if ('.unionfs' in target.children):
        unionmerge(target, target.children['.unionfs']) 
        del target.children['.unionfs']

    #check for aufs
    if ( any ( key.startswith('.wh') for key in target.children.iterkeys() )):
        aufsmerge(target)

    return Manifest(target)
