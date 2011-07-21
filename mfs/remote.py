# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.

"""MFS Remote

methods for basicly everything that doesn't happen locally,
for example:

 * checking for updates
 * fetching manifests
 * fetching datastore contents
"""

def syncDatastore(manifest, local, remote):
    #generate a list of files contained in the manifest
    #check against a list of files already in the local datastore
    #download the missing files form the remote location
    pass

def checkForUpdates(manifest):
    #get the remote location of the manifest
    #check if the remote manifest has been updated
    pass

def getManifest(manifest):
    #download the manifest from the remote side into the local manifest pool
    pass
