#!/usr/bin/python
"""
Utility to detect the containers format.
It tries first to findwell known forensics format and if it cannot find one
it decides that it's a raw image.
"""
import os
import fritutils.termout


def getBuf(fname):
    # return the 512 first bytes of the specified file
    f = open(fname,'ro')
    buf = f.read(512)
    f.close()
    return buf

def detectContainer(containerFile):
    if os.path.isdir(containerFile):
        return 'rofs'
    buf = getBuf(containerFile)
    # search if it's an AFF image
    if buf[0:3] == 'AFF':
        return 'aff'
    elif buf[0:3] == 'EVF':
        return 'ewf'
        
    return 'dd'   
