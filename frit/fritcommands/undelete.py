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
