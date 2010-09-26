#!/usr/bin/python
"""
undelete
This command is used to undelete files from filesystems when possible.
"""
import os
import fritutils

def dirFull(destination):
    if os.path.exists(destination):
        if len(os.listdir(destination)) > 0:
            return True
    
    return False

def factory(Evidences, args):
    for evi in Evidences:
        for fs in evi.fileSystems:
            if dirFull(fs.undeleteDestination):
                fritutils.termout.printWarning('Directory "%s" is not empty. Not trying to undelete.' % fs.undeleteDestination)
            else:
                fs.undelete()
        # As the undelete method locked and maybe mounted the container,
        # we have to remove the undelete lock and umount its container
        # Because it's not handeled by the object to avoid race conditions.
        if evi.isLocked('undelete'):
            evi.umount('undelete')
