#!/usr/bin/python
"""
Compute hashes for the given file.
"""

import subprocess
import os
import os.path
import hashlib
import fritutils.termout
from fritutils.fritglobals import *

BLKSIZE = 512 * 32

def getSsdeep(fullpath):
    ssdeep = subprocess.Popen([SSDEEP, fullpath], stdout=subprocess.PIPE)
    ssdeep.wait()
    sshash = ssdeep.stdout.readlines()[1].split(',')[0]
    return sshash

def getSize(fullpath):
    try:
        stats = os.stat(fullpath)
    except:
        fritutils.termout.printWarning("Problem getting stats on %s" % fullpath)
        return 0
    return stats.st_size

def hashes(fullpath):
    """
    Return a tuple of hexdigests for:
    md5, sha1, sha256
    """
    size = getSize(fullpath)
    if size == 0:
        return("Zero file size", "Zero file size", "Zero file size")
    
    if not os.access(fullpath,os.R_OK):
        return("Unreadable file", "Unreadable file", "Unreadable file")
    
    try:
        fic = open(fullpath,"rb")
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        while 1:
            data = fic.read(BLKSIZE)
            if len(data) == 0:
                break
            md5.update(data)
            sha1.update(data)
            sha256.update(data)
    except (IOError,MemoryError):
        return ("Problematic file", "Problematic file", "Problematic file")
    else:
        return (md5.hexdigest(),sha1.hexdigest(),sha256.hexdigest())
